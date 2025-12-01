"""Tests for utility functions."""

from arkiv import Arkiv


class TestUtilities:
    """Test utility functions."""

    def test_to_seconds_conversion(self, arkiv_client: Arkiv):
        """Test time to seconds conversion."""
        # Test individual units
        assert arkiv_client.arkiv.to_seconds(seconds=60) == 60
        assert arkiv_client.arkiv.to_seconds(minutes=1) == 60
        assert arkiv_client.arkiv.to_seconds(hours=1) == 3600
        assert arkiv_client.arkiv.to_seconds(days=1) == 86400

        # Test combined units
        assert arkiv_client.arkiv.to_seconds(hours=1, minutes=30) == 5400
        assert arkiv_client.arkiv.to_seconds(days=1, hours=12) == 129600

    def test_to_blocks_conversion(self, arkiv_client: Arkiv):
        """Test time to blocks conversion (2 second block time)."""
        # 1 hour = 3600 seconds = 1800 blocks
        assert arkiv_client.arkiv.to_blocks(hours=1) == 1800

        # 1 day = 86400 seconds = 43200 blocks
        assert arkiv_client.arkiv.to_blocks(days=1) == 43200

    def test_entity_exists(self, arkiv_client: Arkiv):
        """Test entity existence check."""
        # Create entity
        entity_key, _ = arkiv_client.arkiv.create_entity(
            payload=b"Existence test",
            content_type="text/plain",
            attributes={"test": "exists"},
            expires_in=arkiv_client.arkiv.to_seconds(hours=1),
        )

        # Should exist
        assert arkiv_client.arkiv.entity_exists(entity_key)

        # Delete it
        arkiv_client.arkiv.delete_entity(entity_key)

        # Should not exist
        assert not arkiv_client.arkiv.entity_exists(entity_key)

    def test_extend_entity(self, arkiv_client: Arkiv):
        """Test entity lifetime extension."""
        # Create entity
        entity_key, _ = arkiv_client.arkiv.create_entity(
            payload=b"Extension test",
            content_type="text/plain",
            attributes={"test": "extend"},
            expires_in=arkiv_client.arkiv.to_seconds(hours=1),
        )

        # Get initial expiration
        entity_before = arkiv_client.arkiv.get_entity(entity_key)
        initial_expiration = entity_before.expires_at_block

        # Extend by 1 hour (in seconds)
        extend_by = arkiv_client.arkiv.to_seconds(hours=1)
        receipt = arkiv_client.arkiv.extend_entity(entity_key, extend_by=extend_by)

        assert len(receipt.extensions) == 1, "Should have one extension event"

        # Verify extended expiration
        entity_after = arkiv_client.arkiv.get_entity(entity_key)
        assert entity_after.expires_at_block > initial_expiration, (
            "Expiration should be extended"
        )


class TestFieldMasks:
    """Test selective field retrieval."""

    def test_get_payload_only(self, arkiv_client: Arkiv):
        """Test retrieving only payload field."""
        from arkiv.types import PAYLOAD

        # Create entity
        entity_key, _ = arkiv_client.arkiv.create_entity(
            payload=b"Payload only test",
            content_type="text/plain",
            attributes={"test": "fields"},
            expires_in=arkiv_client.arkiv.to_seconds(hours=1),
        )

        # Get with payload only
        entity = arkiv_client.arkiv.get_entity(entity_key, fields=PAYLOAD)

        assert entity.payload is not None, "Payload should be retrieved"
        assert entity.content_type is None, "Content type should not be retrieved"
        assert entity.attributes is None, "Attributes should not be retrieved"

    def test_get_attributes_and_owner(self, arkiv_client: Arkiv):
        """Test retrieving specific fields."""
        from arkiv.types import ATTRIBUTES, OWNER

        # Create entity
        entity_key, _ = arkiv_client.arkiv.create_entity(
            payload=b"Fields test",
            content_type="text/plain",
            attributes={"test": "selective"},
            expires_in=arkiv_client.arkiv.to_seconds(hours=1),
        )

        # Get with attributes and owner only
        entity = arkiv_client.arkiv.get_entity(entity_key, fields=ATTRIBUTES | OWNER)

        assert entity.attributes is not None, "Attributes should be retrieved"
        assert entity.owner is not None, "Owner should be retrieved"
        assert entity.payload is None, "Payload should not be retrieved"
