"""
Landing Query Builder for Reconciliation.

Builds SQL queries for reconciliation and KPI calculation in landing database (MySQL).
"""
import logging
from typing import List, Dict, Any
from kg_builder.models import ReconciliationRule, ReconciliationRuleSet

logger = logging.getLogger(__name__)


class LandingQueryBuilder:
    """Builds SQL queries for landing database reconciliation."""

    def __init__(self, db_type: str = "mysql"):
        """
        Initialize query builder.

        Args:
            db_type: Database type (mysql or postgresql)
        """
        self.db_type = db_type.lower()
        if self.db_type not in ["mysql", "postgresql"]:
            raise ValueError(f"Unsupported database type: {db_type}")

    def build_reconciliation_with_kpis_query(
        self,
        source_staging_table: str,
        target_staging_table: str,
        ruleset: ReconciliationRuleSet
    ) -> str:
        """
        Build comprehensive query that performs reconciliation AND calculates KPIs in one query.

        This is the most efficient approach - single query for everything.

        Args:
            source_staging_table: Source staging table name
            target_staging_table: Target staging table name
            ruleset: Reconciliation ruleset

        Returns:
            SQL query string
        """
        # Build join conditions from rules
        join_conditions = []
        confidence_values = []

        for rule in ruleset.rules:
            conditions = []
            for src_col, tgt_col in zip(rule.source_columns, rule.target_columns):
                conditions.append(f"s.`{src_col}` = t.`{tgt_col}`")

            if conditions:
                join_conditions.append(f"({' AND '.join(conditions)})")
                confidence_values.append(rule.confidence_score)

        if not join_conditions:
            raise ValueError("No valid join conditions in ruleset")

        # For simplicity, use first rule's confidence (in production, calculate per-rule)
        avg_confidence = sum(confidence_values) / len(confidence_values)

        query = f"""
        WITH
        -- Count total records in source
        source_total AS (
            SELECT COUNT(*) as total_count
            FROM `{source_staging_table}`
        ),

        -- Count total records in target
        target_total AS (
            SELECT COUNT(*) as total_count
            FROM `{target_staging_table}`
        ),

        -- Find matched records
        matched AS (
            SELECT
                COUNT(*) as matched_count,
                {avg_confidence} as avg_confidence,
                SUM(CASE WHEN {avg_confidence} >= 0.9 THEN 1 ELSE 0 END) as high_conf,
                SUM(CASE WHEN {avg_confidence} >= 0.8 AND {avg_confidence} < 0.9 THEN 1 ELSE 0 END) as med_conf,
                SUM(CASE WHEN {avg_confidence} < 0.8 THEN 1 ELSE 0 END) as low_conf
            FROM `{source_staging_table}` s
            INNER JOIN `{target_staging_table}` t
                ON {' OR '.join(join_conditions)}
        ),

        -- Find unmatched source records
        unmatched_source AS (
            SELECT COUNT(*) as count
            FROM `{source_staging_table}` s
            WHERE NOT EXISTS (
                SELECT 1
                FROM `{target_staging_table}` t
                WHERE {' OR '.join(join_conditions)}
            )
        ),

        -- Find unmatched target records
        unmatched_target AS (
            SELECT COUNT(*) as count
            FROM `{target_staging_table}` t
            WHERE NOT EXISTS (
                SELECT 1
                FROM `{source_staging_table}` s
                WHERE {' OR '.join(join_conditions)}
            )
        ),

        -- Calculate KPIs
        kpis AS (
            SELECT
                m.matched_count,
                us.count as unmatched_source_count,
                ut.count as unmatched_target_count,
                st.total_count as total_source_count,
                tt.total_count as total_target_count,

                -- RCR Calculation
                ROUND((m.matched_count * 100.0 / NULLIF(st.total_count, 0)), 2) as rcr,
                CASE
                    WHEN (m.matched_count * 100.0 / NULLIF(st.total_count, 0)) >= 90 THEN 'HEALTHY'
                    WHEN (m.matched_count * 100.0 / NULLIF(st.total_count, 0)) >= 80 THEN 'WARNING'
                    ELSE 'CRITICAL'
                END as rcr_status,

                -- DQCS Calculation
                ROUND(m.avg_confidence, 3) as dqcs,
                CASE
                    WHEN m.avg_confidence >= 0.8 THEN 'GOOD'
                    WHEN m.avg_confidence >= 0.7 THEN 'ACCEPTABLE'
                    ELSE 'POOR'
                END as dqcs_status,

                -- Confidence distribution
                m.high_conf as high_confidence_count,
                m.med_conf as medium_confidence_count,
                m.low_conf as low_confidence_count,

                -- REI Calculation (simplified)
                ROUND(
                    (m.matched_count * 100.0 / NULLIF(st.total_count, 0)) *
                    ({len(ruleset.rules)} * 1.0 / {max(len(ruleset.rules), 1)})
                , 2) as rei

            FROM matched m
            CROSS JOIN unmatched_source us
            CROSS JOIN unmatched_target ut
            CROSS JOIN source_total st
            CROSS JOIN target_total tt
        )

        SELECT * FROM kpis;
        """

        logger.debug("=" * 80)
        logger.debug("GENERATED RECONCILIATION SQL QUERY:")
        logger.debug("=" * 80)
        logger.debug(query)
        logger.debug("=" * 80)

        return query

    def build_matched_records_query(
        self,
        source_staging_table: str,
        target_staging_table: str,
        rules: List[ReconciliationRule],
        limit: int = 1000
    ) -> str:
        """
        Build query to fetch matched records.

        Args:
            source_staging_table: Source staging table
            target_staging_table: Target staging table
            rules: List of reconciliation rules
            limit: Maximum records to return

        Returns:
            SQL query string
        """
        join_conditions = []
        for rule in rules:
            conditions = []
            for src_col, tgt_col in zip(rule.source_columns, rule.target_columns):
                conditions.append(f"s.`{src_col}` = t.`{tgt_col}`")
            if conditions:
                join_conditions.append(f"({' AND '.join(conditions)})")

        query = f"""
        SELECT
            s.*,
            t.*,
            {rules[0].confidence_score} as match_confidence
        FROM `{source_staging_table}` s
        INNER JOIN `{target_staging_table}` t
            ON {' OR '.join(join_conditions)}
        LIMIT {limit}
        """

        return query

    def build_unmatched_source_query(
        self,
        source_staging_table: str,
        target_staging_table: str,
        rules: List[ReconciliationRule],
        limit: int = 1000
    ) -> str:
        """Build query to fetch unmatched source records."""
        join_conditions = []
        for rule in rules:
            conditions = []
            for src_col, tgt_col in zip(rule.source_columns, rule.target_columns):
                conditions.append(f"s.`{src_col}` = t.`{tgt_col}`")
            if conditions:
                join_conditions.append(f"({' AND '.join(conditions)})")

        query = f"""
        SELECT s.*
        FROM `{source_staging_table}` s
        WHERE NOT EXISTS (
            SELECT 1
            FROM `{target_staging_table}` t
            WHERE {' OR '.join(join_conditions)}
        )
        LIMIT {limit}
        """

        return query

    def build_unmatched_target_query(
        self,
        source_staging_table: str,
        target_staging_table: str,
        rules: List[ReconciliationRule],
        limit: int = 1000
    ) -> str:
        """Build query to fetch unmatched target records."""
        join_conditions = []
        for rule in rules:
            conditions = []
            for src_col, tgt_col in zip(rule.source_columns, rule.target_columns):
                conditions.append(f"s.`{src_col}` = t.`{tgt_col}`")
            if conditions:
                join_conditions.append(f"({' AND '.join(conditions)})")

        query = f"""
        SELECT t.*
        FROM `{target_staging_table}` t
        WHERE NOT EXISTS (
            SELECT 1
            FROM `{source_staging_table}` s
            WHERE {' OR '.join(join_conditions)}
        )
        LIMIT {limit}
        """

        return query

    def build_table_stats_query(self, table_name: str) -> str:
        """Build query to get table statistics."""
        return f"""
        SELECT
            COUNT(*) as row_count,
            COUNT(DISTINCT _staging_id) as unique_records
        FROM `{table_name}`
        """


def get_query_builder(db_type: str = "mysql") -> LandingQueryBuilder:
    """
    Get query builder instance.

    Args:
        db_type: Database type

    Returns:
        LandingQueryBuilder instance
    """
    return LandingQueryBuilder(db_type)
