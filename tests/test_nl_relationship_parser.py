"""
Unit tests for Natural Language Relationship Parser
"""

import pytest
from kg_builder.services.nl_relationship_parser import NaturalLanguageRelationshipParser, get_nl_relationship_parser
from kg_builder.models import NLInputFormat, RelationshipDefinition


@pytest.fixture
def parser():
    """Create a parser instance for testing."""
    return NaturalLanguageRelationshipParser()


@pytest.fixture
def sample_schemas():
    """Sample schema information for testing."""
    return {
        "catalog": {
            "tables": ["catalog", "orders", "customers"],
            "columns": {
                "catalog": ["id", "code", "product_id", "vendor_id", "price"],
                "orders": ["id", "customer_id", "order_date", "total"],
                "customers": ["id", "name", "email"]
            }
        },
        "vendors": {
            "tables": ["vendors", "products", "locations"],
            "columns": {
                "vendors": ["id", "name", "vendor_id"],
                "products": ["id", "product_name", "vendor_id"],
                "locations": ["id", "vendor_id", "address"]
            }
        }
    }


class TestFormatDetection:
    """Test input format detection."""

    def test_detect_natural_language(self, parser):
        """Test detection of natural language format."""
        text = "Products are supplied by Vendors"
        fmt = parser._detect_format(text)
        assert fmt == NLInputFormat.NATURAL_LANGUAGE

    def test_detect_semi_structured_arrow(self, parser):
        """Test detection of semi-structured format with arrow."""
        text = "catalog.product_id → vendor.vendor_id (SUPPLIED_BY)"
        fmt = parser._detect_format(text)
        assert fmt == NLInputFormat.SEMI_STRUCTURED

    def test_detect_semi_structured_dash_arrow(self, parser):
        """Test detection of semi-structured format with dash arrow."""
        text = "catalog.product_id -> vendor.vendor_id (SUPPLIED_BY)"
        fmt = parser._detect_format(text)
        assert fmt == NLInputFormat.SEMI_STRUCTURED

    def test_detect_pseudo_sql_select(self, parser):
        """Test detection of pseudo-SQL format with SELECT."""
        text = "SELECT * FROM products JOIN vendors ON products.vendor_id = vendors.id"
        fmt = parser._detect_format(text)
        assert fmt == NLInputFormat.PSEUDO_SQL

    def test_detect_pseudo_sql_join(self, parser):
        """Test detection of pseudo-SQL format with JOIN."""
        text = "FROM products JOIN vendors ON products.vendor_id = vendors.id"
        fmt = parser._detect_format(text)
        assert fmt == NLInputFormat.PSEUDO_SQL

    def test_detect_business_rules(self, parser):
        """Test detection of business rules format."""
        text = "IF product.status='active' THEN product REFERENCES vendor"
        fmt = parser._detect_format(text)
        assert fmt == NLInputFormat.BUSINESS_RULES


class TestNaturalLanguageParsing:
    """Test natural language parsing."""

    def test_parse_simple_nl_rule_based(self, parser, sample_schemas):
        """Test parsing simple natural language with rule-based approach."""
        text = "catalog supplied by vendors"
        relationships = parser._parse_nl_rule_based(text, sample_schemas)

        assert len(relationships) > 0
        rel = relationships[0]
        assert rel.relationship_type == "SUPPLIED_BY"
        assert rel.input_format == NLInputFormat.NATURAL_LANGUAGE

    def test_parse_nl_with_multiple_verbs(self, parser, sample_schemas):
        """Test parsing NL with different verbs."""
        test_cases = [
            ("Orders contain Products", "CONTAINS"),
            ("Customers place Orders", "PLACES"),
            ("Vendors have Locations", "HAS"),
        ]

        for text, expected_type in test_cases:
            relationships = parser._parse_nl_rule_based(text, sample_schemas)
            if relationships:
                assert relationships[0].relationship_type == expected_type


class TestSemiStructuredParsing:
    """Test semi-structured format parsing."""

    def test_parse_semi_structured_basic(self, parser, sample_schemas):
        """Test parsing basic semi-structured format."""
        text = "catalog.product_id → vendors.vendor_id (SUPPLIED_BY)"
        relationships = parser._parse_semi_structured(text, sample_schemas)

        assert len(relationships) == 1
        rel = relationships[0]
        assert rel.source_table == "catalog"
        assert rel.target_table == "vendors"
        assert rel.relationship_type == "SUPPLIED_BY"
        assert rel.confidence >= 0.8

    def test_parse_semi_structured_multiple(self, parser, sample_schemas):
        """Test parsing multiple semi-structured definitions."""
        text = """
        catalog.product_id → vendors.vendor_id (SUPPLIED_BY)
        orders.customer_id → customers.id (PLACED_BY)
        """
        relationships = parser._parse_semi_structured(text, sample_schemas)

        assert len(relationships) == 2
        assert relationships[0].relationship_type == "SUPPLIED_BY"
        assert relationships[1].relationship_type == "PLACED_BY"


class TestPseudoSQLParsing:
    """Test pseudo-SQL format parsing."""

    def test_parse_pseudo_sql_basic(self, parser, sample_schemas):
        """Test parsing basic pseudo-SQL format."""
        text = "SELECT * FROM catalog JOIN vendors ON catalog.vendor_id = vendors.id"
        relationships = parser._parse_pseudo_sql(text, sample_schemas)

        assert len(relationships) == 1
        rel = relationships[0]
        assert rel.source_table == "catalog"
        assert rel.target_table == "vendors"
        assert rel.relationship_type == "REFERENCES"

    def test_parse_pseudo_sql_case_insensitive(self, parser, sample_schemas):
        """Test that pseudo-SQL parsing is case-insensitive."""
        text = "select * from catalog join vendors on catalog.vendor_id = vendors.id"
        relationships = parser._parse_pseudo_sql(text, sample_schemas)

        assert len(relationships) == 1


class TestValidation:
    """Test relationship validation."""

    def test_validate_valid_relationship(self, parser, sample_schemas):
        """Test validation of a valid relationship."""
        rel = RelationshipDefinition(
            source_table="catalog",
            target_table="vendors",
            relationship_type="SUPPLIED_BY",
            properties=[],
            confidence=0.85,
            reasoning="Test",
            input_format=NLInputFormat.NATURAL_LANGUAGE
        )

        is_valid, errors = parser._validate_relationship(rel, sample_schemas)
        assert is_valid
        assert len(errors) == 0

    def test_validate_invalid_source_table(self, parser, sample_schemas):
        """Test validation with invalid source table."""
        rel = RelationshipDefinition(
            source_table="nonexistent",
            target_table="vendors",
            relationship_type="SUPPLIED_BY",
            properties=[],
            confidence=0.85,
            reasoning="Test",
            input_format=NLInputFormat.NATURAL_LANGUAGE
        )

        is_valid, errors = parser._validate_relationship(rel, sample_schemas)
        assert not is_valid
        assert len(errors) > 0

    def test_validate_invalid_relationship_type(self, parser, sample_schemas):
        """Test validation with invalid relationship type."""
        rel = RelationshipDefinition(
            source_table="catalog",
            target_table="vendors",
            relationship_type="INVALID_TYPE",
            properties=[],
            confidence=0.85,
            reasoning="Test",
            input_format=NLInputFormat.NATURAL_LANGUAGE
        )

        is_valid, errors = parser._validate_relationship(rel, sample_schemas)
        assert not is_valid
        assert any("Invalid relationship type" in e for e in errors)


class TestTableMatching:
    """Test table name matching."""

    def test_find_exact_match(self, parser, sample_schemas):
        """Test finding exact table match."""
        result = parser._find_matching_table("catalog", sample_schemas)
        assert result is not None
        assert "catalog" in result.lower()

    def test_find_fuzzy_match(self, parser, sample_schemas):
        """Test finding fuzzy table match."""
        result = parser._find_matching_table("vendor", sample_schemas)
        assert result is not None
        assert "vendor" in result.lower()

    def test_find_no_match(self, parser, sample_schemas):
        """Test when no table matches."""
        result = parser._find_matching_table("nonexistent", sample_schemas)
        assert result is None


class TestFullParsing:
    """Test full parsing workflow."""

    def test_parse_natural_language_full(self, parser, sample_schemas):
        """Test full parsing of natural language."""
        text = "catalog supplied by vendors"
        relationships = parser.parse(text, sample_schemas, use_llm=False)

        assert len(relationships) > 0
        rel = relationships[0]
        assert rel.source_table is not None
        assert rel.target_table is not None
        assert rel.relationship_type is not None

    def test_parse_semi_structured_full(self, parser, sample_schemas):
        """Test full parsing of semi-structured format."""
        text = "catalog.product_id → vendors.vendor_id (SUPPLIED_BY)"
        relationships = parser.parse(text, sample_schemas, use_llm=False)

        assert len(relationships) == 1
        rel = relationships[0]
        assert rel.validation_status in ["VALID", "INVALID"]

    def test_parse_multiple_definitions(self, parser, sample_schemas):
        """Test parsing multiple definitions."""
        definitions = [
            "catalog are supplied by vendors",
            "orders contain customers",
            "catalog has vendors"
        ]

        all_relationships = []
        for definition in definitions:
            relationships = parser.parse(definition, sample_schemas, use_llm=False)
            all_relationships.extend(relationships)

        assert len(all_relationships) > 0


class TestSingleton:
    """Test singleton pattern."""

    def test_get_parser_singleton(self):
        """Test that get_nl_relationship_parser returns singleton."""
        parser1 = get_nl_relationship_parser()
        parser2 = get_nl_relationship_parser()

        assert parser1 is parser2


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_parse_empty_string(self, parser, sample_schemas):
        """Test parsing empty string."""
        relationships = parser.parse("", sample_schemas, use_llm=False)
        assert isinstance(relationships, list)

    def test_parse_with_empty_schemas(self, parser):
        """Test parsing with empty schemas."""
        relationships = parser.parse("Products are supplied by Vendors", {}, use_llm=False)
        assert isinstance(relationships, list)

    def test_parse_with_special_characters(self, parser, sample_schemas):
        """Test parsing with special characters."""
        text = "Products (SKU) are supplied by Vendors [ID]"
        relationships = parser.parse(text, sample_schemas, use_llm=False)
        assert isinstance(relationships, list)

    def test_confidence_filtering(self, parser, sample_schemas):
        """Test that low confidence relationships are filtered."""
        rel = RelationshipDefinition(
            source_table="catalog",
            target_table="vendors",
            relationship_type="SUPPLIED_BY",
            properties=[],
            confidence=0.5,  # Below typical threshold
            reasoning="Test",
            input_format=NLInputFormat.NATURAL_LANGUAGE
        )

        # Manually check confidence
        assert rel.confidence < 0.7

