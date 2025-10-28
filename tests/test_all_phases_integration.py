"""
Comprehensive Integration Tests for All Phases

Tests Phase 1-4 implementation:
- Phase 1: Direct SQL generation via LLM
- Phase 2: WHERE clause intelligence with complex operators
- Phase 3: LLM-based JOIN path optimization
- Phase 4: Complex query support (GROUP BY, ORDER BY, LIMIT)
"""

import pytest
from unittest.mock import Mock, patch
from kg_builder.services.nl_query_parser import QueryIntent, Filter, OrderBy
from kg_builder.services.nl_sql_generator import get_nl_sql_generator
from kg_builder.services.llm_path_optimizer import get_llm_path_optimizer
from kg_builder.models import KnowledgeGraph, GraphNode, GraphRelationship


@pytest.fixture
def sample_kg():
    """Create a sample Knowledge Graph for testing."""
    return KnowledgeGraph(
        name="test_kg",
        nodes=[
            GraphNode(id="table_products", label="Table", properties={}),
            GraphNode(id="table_categories", label="Table", properties={}),
            GraphNode(id="table_suppliers", label="Table", properties={})
        ],
        relationships=[
            GraphRelationship(
                source_id="table_products",
                target_id="table_categories",
                relationship_type="REFERENCES",
                properties={},
                source_column="category_id",
                target_column="id"
            ),
            GraphRelationship(
                source_id="table_products",
                target_id="table_suppliers",
                relationship_type="REFERENCES",
                properties={},
                source_column="supplier_id",
                target_column="id"
            )
        ],
        schema_file="test",
        metadata={},
        table_aliases={}
    )


class TestPhase2ComplexOperators:
    """Test Phase 2: Complex operator support."""

    def test_filter_with_greater_than(self, sample_kg):
        """Test > operator."""
        intent = QueryIntent(
            definition="Show products with price > 100",
            query_type="filter_query",
            source_table="products",
            filters_v2=[Filter(column="price", operator=">", value=100)]
        )

        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=False)
        sql = generator.generate(intent)

        assert "> 100" in sql or ">= 100" in sql

    def test_filter_with_like(self, sample_kg):
        """Test LIKE operator."""
        intent = QueryIntent(
            definition="Show products like 'Apple'",
            query_type="filter_query",
            source_table="products",
            filters_v2=[Filter(column="name", operator="LIKE", value="Apple")]
        )

        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=False)
        sql = generator.generate(intent)

        assert "LIKE" in sql.upper()
        assert "Apple" in sql

    def test_filter_with_in(self, sample_kg):
        """Test IN operator."""
        intent = QueryIntent(
            definition="Show products in categories A, B, C",
            query_type="filter_query",
            source_table="products",
            filters_v2=[Filter(column="category", operator="IN", value=["A", "B", "C"])]
        )

        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=False)
        sql = generator.generate(intent)

        assert "IN" in sql.upper()
        assert "'A'" in sql
        assert "'B'" in sql
        assert "'C'" in sql

    def test_filter_with_between(self, sample_kg):
        """Test BETWEEN operator."""
        intent = QueryIntent(
            definition="Show products with price between 100 and 500",
            query_type="filter_query",
            source_table="products",
            filters_v2=[Filter(column="price", operator="BETWEEN", value=[100, 500])]
        )

        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=False)
        sql = generator.generate(intent)

        assert "BETWEEN" in sql.upper()
        assert "100" in sql
        assert "500" in sql

    def test_filter_with_is_null(self, sample_kg):
        """Test IS NULL operator."""
        intent = QueryIntent(
            definition="Show products with no supplier",
            query_type="filter_query",
            source_table="products",
            filters_v2=[Filter(column="supplier_id", operator="IS NULL", value=None)]
        )

        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=False)
        sql = generator.generate(intent)

        assert "IS NULL" in sql.upper()

    def test_multiple_filters_with_and(self, sample_kg):
        """Test multiple filters with AND logic."""
        intent = QueryIntent(
            definition="Show active products with price > 100",
            query_type="filter_query",
            source_table="products",
            filters_v2=[
                Filter(column="status", operator="=", value="active", logic="AND"),
                Filter(column="price", operator=">", value=100, logic="AND")
            ]
        )

        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=False)
        sql = generator.generate(intent)

        assert "status" in sql.lower()
        assert "active" in sql
        assert "price" in sql.lower()
        assert "> 100" in sql or ">= 100" in sql


class TestPhase3JoinPathOptimization:
    """Test Phase 3: LLM-based JOIN path optimization."""

    @patch('kg_builder.services.llm_path_optimizer.get_llm_service')
    def test_path_scoring_with_llm(self, mock_llm_service, sample_kg):
        """Test LLM-based path scoring."""
        # Mock LLM service
        mock_service = Mock()
        mock_service.is_enabled.return_value = True

        # Mock LLM response for path scoring
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='''
{
    "best_path": ["products", "categories"],
    "score": 95,
    "reasoning": "Direct foreign key relationship with 1:N cardinality"
}
        '''))]
        mock_service.create_chat_completion.return_value = mock_response
        mock_llm_service.return_value = mock_service

        # Test path optimizer
        optimizer = get_llm_path_optimizer(kg=sample_kg)
        paths = [
            ["products", "suppliers", "categories"],  # Longer path
            ["products", "categories"]  # Shorter, direct path
        ]

        best_path = optimizer.score_paths("products", "categories", paths)

        assert best_path == ["products", "categories"]

    def test_path_scoring_fallback_to_shortest(self, sample_kg):
        """Test fallback to shortest path when LLM disabled."""
        optimizer = get_llm_path_optimizer(kg=sample_kg)

        paths = [
            ["products", "suppliers", "categories"],  # Length 3
            ["products", "categories"]  # Length 2 (shortest)
        ]

        best_path = optimizer.score_paths("products", "categories", paths)

        # Should return shortest path as fallback
        assert len(best_path) == 2

    def test_single_path_returns_immediately(self, sample_kg):
        """Test that single path is returned without scoring."""
        optimizer = get_llm_path_optimizer(kg=sample_kg)

        paths = [["products", "categories"]]

        best_path = optimizer.score_paths("products", "categories", paths)

        assert best_path == ["products", "categories"]


class TestPhase4ComplexQueries:
    """Test Phase 4: Complex query support."""

    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_group_by_with_llm(self, mock_llm_service, sample_kg):
        """Test GROUP BY query generation."""
        # Mock LLM service
        mock_service = Mock()
        mock_service.is_enabled.return_value = True

        # Mock SQL generation response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="""
SELECT `category`, COUNT(*) as count
FROM `products`
GROUP BY `category`
        """))]
        mock_service.create_chat_completion.return_value = mock_response
        mock_llm_service.return_value = mock_service

        intent = QueryIntent(
            definition="Count products by category",
            query_type="aggregation_query",
            source_table="products",
            group_by_columns=["category"]
        )

        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=True)
        sql = generator.generate(intent)

        assert "GROUP BY" in sql.upper()
        assert "category" in sql.lower()
        assert "COUNT" in sql.upper()

    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_order_by_with_llm(self, mock_llm_service, sample_kg):
        """Test ORDER BY query generation."""
        # Mock LLM service
        mock_service = Mock()
        mock_service.is_enabled.return_value = True

        # Mock SQL generation response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="""
SELECT * FROM `products`
ORDER BY `price` DESC, `name` ASC
        """))]
        mock_service.create_chat_completion.return_value = mock_response
        mock_llm_service.return_value = mock_service

        intent = QueryIntent(
            definition="Show products ordered by price descending",
            query_type="data_query",
            source_table="products",
            order_by=[
                OrderBy(column="price", direction="DESC"),
                OrderBy(column="name", direction="ASC")
            ]
        )

        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=True)
        sql = generator.generate(intent)

        assert "ORDER BY" in sql.upper()
        assert "price" in sql.lower()
        assert "DESC" in sql.upper()

    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_limit_and_offset(self, mock_llm_service, sample_kg):
        """Test LIMIT and OFFSET."""
        # Mock LLM service
        mock_service = Mock()
        mock_service.is_enabled.return_value = True

        # Mock SQL generation response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="""
SELECT * FROM `products`
LIMIT 10 OFFSET 20
        """))]
        mock_service.create_chat_completion.return_value = mock_response
        mock_llm_service.return_value = mock_service

        intent = QueryIntent(
            definition="Show 10 products starting from 20",
            query_type="data_query",
            source_table="products",
            limit=10,
            offset=20
        )

        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=True)
        sql = generator.generate(intent)

        assert "LIMIT" in sql.upper()
        assert "10" in sql
        # OFFSET may or may not be present depending on database

    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_having_clause(self, mock_llm_service, sample_kg):
        """Test HAVING clause for aggregate filtering."""
        # Mock LLM service
        mock_service = Mock()
        mock_service.is_enabled.return_value = True

        # Mock SQL generation response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="""
SELECT `category`, COUNT(*) as count
FROM `products`
GROUP BY `category`
HAVING count > 10
        """))]
        mock_service.create_chat_completion.return_value = mock_response
        mock_llm_service.return_value = mock_service

        intent = QueryIntent(
            definition="Show categories with more than 10 products",
            query_type="aggregation_query",
            source_table="products",
            group_by_columns=["category"],
            having_conditions=[Filter(column="count", operator=">", value=10)]
        )

        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=True)
        sql = generator.generate(intent)

        assert "GROUP BY" in sql.upper()
        assert "HAVING" in sql.upper()


class TestAllPhasesEndToEnd:
    """End-to-end tests combining all phases."""

    @patch('kg_builder.services.llm_sql_generator.get_llm_service')
    def test_complex_query_all_features(self, mock_llm_service, sample_kg):
        """Test complex query with filters, GROUP BY, HAVING, ORDER BY, LIMIT."""
        # Mock LLM service
        mock_service = Mock()
        mock_service.is_enabled.return_value = True

        # Mock comprehensive SQL response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="""
SELECT `category`, `supplier_id`, COUNT(*) as product_count, AVG(`price`) as avg_price
FROM `products`
WHERE `status` = 'active' AND `price` > 100
GROUP BY `category`, `supplier_id`
HAVING product_count > 5 AND avg_price > 200
ORDER BY product_count DESC, avg_price DESC
LIMIT 20
        """))]
        mock_service.create_chat_completion.return_value = mock_response
        mock_llm_service.return_value = mock_service

        intent = QueryIntent(
            definition="Show top 20 categories with suppliers having more than 5 active products priced over 100, ordered by count",
            query_type="aggregation_query",
            source_table="products",
            filters_v2=[
                Filter(column="status", operator="=", value="active"),
                Filter(column="price", operator=">", value=100)
            ],
            group_by_columns=["category", "supplier_id"],
            having_conditions=[
                Filter(column="product_count", operator=">", value=5),
                Filter(column="avg_price", operator=">", value=200)
            ],
            order_by=[
                OrderBy(column="product_count", direction="DESC"),
                OrderBy(column="avg_price", direction="DESC")
            ],
            limit=20
        )

        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=True)
        sql = generator.generate(intent)

        # Verify all components present
        assert "WHERE" in sql.upper()
        assert "GROUP BY" in sql.upper()
        assert "HAVING" in sql.upper()
        assert "ORDER BY" in sql.upper()
        assert "LIMIT" in sql.upper()


class TestBackwardCompatibility:
    """Test backward compatibility with legacy filter format."""

    def test_legacy_filter_format_still_works(self, sample_kg):
        """Test that old dict format filters still work."""
        intent = QueryIntent(
            definition="Show active products",
            query_type="filter_query",
            source_table="products",
            filters=[{"column": "status", "value": "active"}]  # Legacy format
        )

        generator = get_nl_sql_generator(db_type="mysql", kg=sample_kg, use_llm=False)
        sql = generator.generate(intent)

        assert "status" in sql.lower()
        assert "active" in sql

    def test_automatic_conversion_to_filters_v2(self, sample_kg):
        """Test that legacy filters are converted to filters_v2."""
        intent = QueryIntent(
            definition="Show active products",
            query_type="filter_query",
            source_table="products",
            filters=[
                {"column": "status", "operator": "=", "value": "active"},
                {"column": "price", "operator": ">", "value": 100}
            ]
        )

        # After __post_init__, filters_v2 should be populated
        assert len(intent.filters_v2) == 2
        assert intent.filters_v2[0].column == "status"
        assert intent.filters_v2[0].operator == "="
        assert intent.filters_v2[1].column == "price"
        assert intent.filters_v2[1].operator == ">"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
