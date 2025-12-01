"""Tests for Example 4: Entity CRUD Operations."""

from arkiv import Arkiv


class TestEntityCRUD:
    """Test entity CRUD operations from example 04."""

    def test_create_entity(self, arkiv_client: Arkiv, test_payload, test_attributes):
        """Test entity creation."""
        entity_key, receipt = arkiv_client.arkiv.create_entity(
            payload=test_payload,
            content_type="text/plain",
            attributes=test_attributes,
            expires_in=arkiv_client.arkiv.to_seconds(hours=1),
        )

        assert entity_key is not None, "Entity key should be generated"
        assert receipt.tx_hash is not None, "Transaction hash should exist"
        assert receipt.block_number > 0, "Should be mined in a block"
        assert len(receipt.creates) == 1, "Should have one create event"

    def test_read_entity(self, arkiv_client: Arkiv, test_payload, test_attributes):
        """Test reading a created entity."""
        # Create entity first
        entity_key, _ = arkiv_client.arkiv.create_entity(
            payload=test_payload,
            content_type="text/plain",
            attributes=test_attributes,
            expires_in=arkiv_client.arkiv.to_seconds(hours=1),
        )

        # Read it back
        entity = arkiv_client.arkiv.get_entity(entity_key)

        assert entity.key == entity_key, "Entity key should match"
        assert entity.payload == test_payload, "Payload should match"
        assert entity.content_type == "text/plain", "Content type should match"
        assert entity.owner == arkiv_client.eth.default_account, "Owner should match"

    def test_update_entity(self, arkiv_client: Arkiv, test_payload, test_attributes):
        """Test updating an entity."""
        # Create entity
        entity_key, _ = arkiv_client.arkiv.create_entity(
            payload=test_payload,
            content_type="text/plain",
            attributes=test_attributes,
            expires_in=arkiv_client.arkiv.to_seconds(hours=1),
        )

        # Update it
        new_payload = b"Updated test payload"
        receipt = arkiv_client.arkiv.update_entity(
            entity_key=entity_key,
            payload=new_payload,
            content_type="text/plain",
            attributes=test_attributes,
            expires_in=arkiv_client.arkiv.to_seconds(hours=2),
        )

        assert receipt.tx_hash is not None, "Update should have transaction hash"
        assert len(receipt.updates) == 1, "Should have one update event"

        # Verify update
        entity = arkiv_client.arkiv.get_entity(entity_key)
        assert entity.payload == new_payload, "Payload should be updated"

    def test_delete_entity(self, arkiv_client: Arkiv, test_payload, test_attributes):
        """Test deleting an entity."""
        # Create entity
        entity_key, _ = arkiv_client.arkiv.create_entity(
            payload=test_payload,
            content_type="text/plain",
            attributes=test_attributes,
            expires_in=arkiv_client.arkiv.to_seconds(hours=1),
        )

        # Delete it
        receipt = arkiv_client.arkiv.delete_entity(entity_key)

        assert receipt.tx_hash is not None, "Delete should have transaction hash"
        assert len(receipt.deletes) == 1, "Should have one delete event"

        # Verify deletion
        assert not arkiv_client.arkiv.entity_exists(entity_key), (
            "Entity should no longer exist"
        )

    def test_full_crud_cycle(self, arkiv_client: Arkiv):
        """Test complete CRUD cycle."""
        # Create
        payload = b"Full cycle test"
        entity_key, create_receipt = arkiv_client.arkiv.create_entity(
            payload=payload,
            content_type="text/plain",
            attributes={"cycle": "full"},
            expires_in=arkiv_client.arkiv.to_seconds(hours=1),
        )

        # Read
        entity = arkiv_client.arkiv.get_entity(entity_key)
        assert entity.payload == payload

        # Update
        new_payload = b"Full cycle updated"
        update_receipt = arkiv_client.arkiv.update_entity(
            entity_key=entity_key,
            payload=new_payload,
            content_type="text/plain",
            attributes={"cycle": "full", "updated": 1},
            expires_in=arkiv_client.arkiv.to_seconds(hours=2),
        )
        assert update_receipt.updates[0].key == entity_key

        # Verify update
        entity = arkiv_client.arkiv.get_entity(entity_key)
        assert entity.payload == new_payload

        # Delete
        delete_receipt = arkiv_client.arkiv.delete_entity(entity_key)
        assert delete_receipt.deletes[0].key == entity_key

        # Verify deletion
        assert not arkiv_client.arkiv.entity_exists(entity_key)
