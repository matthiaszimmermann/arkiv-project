"""Tests for querying functionality (Example 5)."""

from typing import cast
from arkiv import Arkiv
from arkiv.types import Attributes


class TestQuerying:
    """Test query operations from example 05."""

    def test_query_by_owner(self, arkiv_client: Arkiv):
        """Test querying entities by owner."""
        # Create test entities
        for i in range(3):
            arkiv_client.arkiv.create_entity(
                payload=f"Query test {i}".encode(),
                content_type="text/plain",
                attributes=cast(Attributes, {"test": "query"}),
                expires_in=arkiv_client.arkiv.to_seconds(hours=1),
            )

        # Query by owner
        owner = arkiv_client.eth.default_account
        results = list(arkiv_client.arkiv.query_entities(f'$owner = "{owner}"'))

        assert len(results) >= 3, "Should find at least the 3 created entities"

    def test_query_by_content_type(self, arkiv_client: Arkiv):
        """Test querying by content type (client-side filtering until node supports it)."""
        # Create entities with different content types
        arkiv_client.arkiv.create_entity(
            payload=b"Text entity",
            content_type="text/plain",
            attributes=cast(Attributes, {"type": "text"}),
            expires_in=arkiv_client.arkiv.to_seconds(hours=1),
        )

        arkiv_client.arkiv.create_entity(
            payload=b'{"key": "value"}',
            content_type="application/json",
            attributes=cast(Attributes, {"type": "json"}),
            expires_in=arkiv_client.arkiv.to_seconds(hours=1),
        )

        # Query all entities and filter client-side
        # Note: $content_type query support may not be available in all node versions
        all_results = list(
            arkiv_client.arkiv.query_entities(f'$owner = "{arkiv_client.eth.default_account}"')
        )
        
        text_results = [e for e in all_results if e.content_type == "text/plain"]
        assert len(text_results) >= 1, "Should find text/plain entities"

        json_results = [e for e in all_results if e.content_type == "application/json"]
        assert len(json_results) >= 1, "Should find application/json entities"

    def test_query_by_custom_attributes(self, arkiv_client: Arkiv):
        """Test querying by user-defined attributes."""
        # Create entities with custom attributes
        arkiv_client.arkiv.create_entity(
            payload=b"Active entity",
            content_type="text/plain",
            attributes=cast(Attributes, {"status": "active", "priority": 1}),
            expires_in=arkiv_client.arkiv.to_seconds(hours=1),
        )

        arkiv_client.arkiv.create_entity(
            payload=b"Inactive entity",
            content_type="text/plain",
            attributes=cast(Attributes, {"status": "inactive", "priority": 2}),
            expires_in=arkiv_client.arkiv.to_seconds(hours=1),
        )

        # Query for active status
        active_results = list(arkiv_client.arkiv.query_entities('status = "active"'))
        assert len(active_results) >= 1, "Should find active entities"

        # Query for high priority
        priority_results = list(arkiv_client.arkiv.query_entities("priority = 1"))
        assert len(priority_results) >= 1, "Should find priority 1 entities"

    def test_query_with_pagination(self, arkiv_client: Arkiv):
        """Test query pagination."""
        from arkiv.types import QueryOptions

        # Create multiple entities
        for i in range(5):
            arkiv_client.arkiv.create_entity(
                payload=f"Pagination test {i}".encode(),
                content_type="text/plain",
                attributes=cast(Attributes, {"test": "pagination"}),
                expires_in=arkiv_client.arkiv.to_seconds(hours=1),
            )

        # Query with limit
        result = arkiv_client.arkiv.query_entities_page(
            'test = "pagination"', options=QueryOptions(max_results_per_page=2)
        )

        assert len(result.entities) <= 2, "Should respect max_results_per_page"

    def test_query_combined_conditions(self, arkiv_client: Arkiv):
        """Test query with multiple conditions."""
        # Create test entities
        arkiv_client.arkiv.create_entity(
            payload=b"Match all conditions",
            content_type="text/plain",
            attributes=cast(Attributes, {"category": "test", "status": "active", "version": 1}),
            expires_in=arkiv_client.arkiv.to_seconds(hours=1),
        )

        arkiv_client.arkiv.create_entity(
            payload=b"Match some conditions",
            content_type="text/plain",
            attributes=cast(Attributes, {"category": "test", "status": "inactive", "version": 1}),
            expires_in=arkiv_client.arkiv.to_seconds(hours=1),
        )

        # Query with AND condition
        results = list(
            arkiv_client.arkiv.query_entities('category = "test" AND status = "active"')
        )

        assert len(results) >= 1, "Should find entities matching all conditions"
        for entity in results:
            assert entity.attributes is not None
            assert entity.attributes.get("category") == "test"
            assert entity.attributes.get("status") == "active"
