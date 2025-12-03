"""
Arkiv Locust User Class

Custom Locust User that uses the Arkiv SDK to interact with an Arkiv network.
This replaces the standard HttpUser with blockchain-specific behavior.
"""

import json
import os
import time
import uuid
from typing import Any, Optional, cast

from dotenv import load_dotenv
from locust import User, task, between, events
from locust.exception import StopUser
from web3.providers.base import BaseProvider

from arkiv import Arkiv, NamedAccount
from arkiv.provider import ProviderBuilder
from arkiv.types import Attributes

# Load environment variables from .env file
load_dotenv()

# Default RPC URL (can be overridden via .env or --host)
DEFAULT_RPC_URL = os.getenv("ARKIV_RPC_URL", "https://mendoza.hoodi.arkiv.network/rpc")


class ArkivUser(User):
    """
    A Locust User that performs Arkiv operations.
    
    Each user instance gets its own funded account and performs
    create, read, query, and update operations against the Arkiv network.
    """
    
    # Wait 0.5-2 seconds between tasks
    wait_time = between(0.5, 2)
    
    # Will be set from environment or command line
    host: str = ""
    
    # Track created entities for later operations
    created_entities: list[str]
    
    # Arkiv client instance
    client: Optional[Arkiv] = None
    account: Optional[NamedAccount] = None
    
    def on_start(self) -> None:
        """Called when a User starts - initialize Arkiv client with unique account."""
        try:
            # Create unique account for this user
            user_id = f"loadtest-{uuid.uuid4().hex[:8]}"
            self.account = NamedAccount.create(user_id)
            self.created_entities = []
            
            # Connect to the target Arkiv network
            rpc_url = self.host or DEFAULT_RPC_URL
            provider = cast(BaseProvider, ProviderBuilder().custom(url=rpc_url).build())
            
            self.client = Arkiv(provider=provider, account=self.account)
            
            # Log successful connection
            balance = self.client.eth.get_balance(self.account.address)
            print(f"🚀 User {user_id} connected | Balance: {balance / 10**18:.4f} ETH")
            
            if balance == 0:
                print(f"⚠️  Warning: Account {self.account.address} has zero balance - transactions will fail!")
            
        except Exception as e:
            print(f"❌ Failed to initialize Arkiv client: {e}")
            raise StopUser()
    
    def on_stop(self) -> None:
        """Called when a User stops - cleanup resources."""
        if self.client:
            try:
                self.client.arkiv.cleanup_filters()
            except Exception:
                pass
        print(f"👋 User stopped | Created {len(self.created_entities)} entities")
    
    def _fire_event(
        self,
        request_type: str,
        name: str,
        response_time: float,
        response_length: int = 0,
        exception: Optional[Exception] = None
    ) -> None:
        """Fire a Locust request event for metrics tracking."""
        events.request.fire(
            request_type=request_type,
            name=name,
            response_time=response_time,
            response_length=response_length,
            exception=exception,
            context={},
        )
    
    @task(5)
    def create_entity(self) -> None:
        """Create a new entity on the Arkiv network."""
        if not self.client:
            return
        
        start_time = time.time()
        exception: Optional[Exception] = None
        
        try:
            # Create entity with random payload
            payload = json.dumps({
                "test_id": uuid.uuid4().hex,
                "timestamp": time.time(),
                "user": self.account.name if self.account else "unknown",
                "type": "loadtest"
            }).encode()
            
            entity_key, receipt = self.client.arkiv.create_entity(
                payload=payload,
                content_type="application/json",
                expires_in=self.client.arkiv.to_seconds(hours=1),
                attributes=Attributes({
                    "test_type": "loadtest",
                    "user": self.account.name if self.account else "unknown"
                })
            )
            
            # Track created entity for later operations
            self.created_entities.append(entity_key)
            
            # Keep list manageable
            if len(self.created_entities) > 100:
                self.created_entities = self.created_entities[-50:]
            
        except Exception as e:
            exception = e
        
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        self._fire_event("arkiv", "create_entity", response_time, exception=exception)
    
    @task(3)
    def read_entity(self) -> None:
        """Read an existing entity from the network."""
        if not self.client or not self.created_entities:
            return
        
        start_time = time.time()
        exception: Optional[Exception] = None
        response_length = 0
        
        try:
            # Pick a random entity we created
            import random
            entity_key = random.choice(self.created_entities)
            
            entity = self.client.arkiv.get_entity(entity_key)
            if entity and entity.payload:
                response_length = len(entity.payload)
            
        except ValueError:
            # Entity not found (may have expired) - remove from list
            if entity_key in self.created_entities:
                self.created_entities.remove(entity_key)
        except Exception as e:
            exception = e
        
        response_time = (time.time() - start_time) * 1000
        self._fire_event("arkiv", "read_entity", response_time, response_length, exception)
    
    @task(2)
    def query_entities(self) -> None:
        """Query entities owned by this user."""
        if not self.client or not self.account:
            return
        
        start_time = time.time()
        exception: Optional[Exception] = None
        response_length = 0
        
        try:
            # Query all entities with our test_type attribute
            query = 'test_type = "loadtest"'
            entities = list(self.client.arkiv.query_entities(query))
            response_length = len(entities)
            
        except Exception as e:
            exception = e
        
        response_time = (time.time() - start_time) * 1000
        self._fire_event("arkiv", "query_entities", response_time, response_length, exception)
    
    @task(1)
    def check_entity_exists(self) -> None:
        """Check if an entity exists."""
        if not self.client or not self.created_entities:
            return
        
        start_time = time.time()
        exception: Optional[Exception] = None
        
        try:
            import random
            entity_key = random.choice(self.created_entities)
            exists = self.client.arkiv.entity_exists(entity_key)
            
            # Clean up our list if entity no longer exists
            if not exists and entity_key in self.created_entities:
                self.created_entities.remove(entity_key)
            
        except Exception as e:
            exception = e
        
        response_time = (time.time() - start_time) * 1000
        self._fire_event("arkiv", "entity_exists", response_time, exception=exception)


class ArkivWriteHeavyUser(ArkivUser):
    """
    A write-heavy user variant for testing write throughput.
    90% creates, 10% reads.
    """
    
    @task(9)
    def create_entity(self) -> None:
        super().create_entity()
    
    @task(1)
    def read_entity(self) -> None:
        super().read_entity()
    
    # Override to disable other tasks
    def query_entities(self) -> None:
        pass
    
    def check_entity_exists(self) -> None:
        pass


class ArkivReadHeavyUser(ArkivUser):
    """
    A read-heavy user variant for testing read throughput.
    20% creates, 80% reads/queries.
    """
    
    @task(2)
    def create_entity(self) -> None:
        super().create_entity()
    
    @task(5)
    def read_entity(self) -> None:
        super().read_entity()
    
    @task(3)
    def query_entities(self) -> None:
        super().query_entities()
