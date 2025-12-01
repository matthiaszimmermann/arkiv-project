"""Tests for Example 3: Client Initialization Patterns."""

import pytest
from arkiv import Arkiv, NamedAccount
from arkiv.provider import ProviderBuilder
from typing import cast
from web3.providers.base import BaseProvider


def test_default_client(arkiv_node):
    """Test default client initialization with shared node."""
    # Use provider connected to shared test node
    provider = cast(BaseProvider, ProviderBuilder().node(arkiv_node).build())
    account = NamedAccount.create("test-default-client")
    arkiv_node.fund_account(account)
    client = Arkiv(provider, account=account)
    
    assert client is not None
    assert client.eth.default_account is not None
    
    # Verify account is funded
    balance = client.eth.get_balance(client.eth.default_account)
    assert balance > 0
    
    # Test basic operation
    entity_key, receipt = client.arkiv.create_entity(
        payload=b"Test from default client",
        content_type="text/plain",
        expires_in=3600
    )
    assert entity_key is not None
    assert receipt.block_number > 0


def test_custom_provider(arkiv_node):
    """Test custom provider initialization."""
    provider = cast(BaseProvider, ProviderBuilder().custom(url=arkiv_node.http_url).build())
    custom_client = Arkiv(provider)
    
    assert custom_client is not None
    # Note: Client with only provider doesn't have default account
    # This is expected behavior


def test_custom_account(arkiv_node):
    """Test custom account initialization."""
    provider = cast(BaseProvider, ProviderBuilder().custom(url=arkiv_node.http_url).build())
    account = NamedAccount.create("test-custom-account")
    arkiv_node.fund_account(account)
    
    custom_client = Arkiv(provider, account=account)
    
    assert custom_client.eth.default_account == account.address
    
    # Verify account is funded and operational
    balance = custom_client.eth.get_balance(account.address)
    assert balance > 0
    
    # Test operation with custom account
    entity_key, receipt = custom_client.arkiv.create_entity(
        payload=b"Test from custom account",
        content_type="text/plain",
        expires_in=3600
    )
    assert entity_key is not None
    
    # Verify owner is the custom account
    entity = custom_client.arkiv.get_entity(entity_key)
    assert entity is not None
    assert entity.owner == account.address


def test_multiple_accounts_switch_to(arkiv_node):
    """Test managing multiple accounts with switch_to()."""
    # Create client with node
    provider = cast(BaseProvider, ProviderBuilder().node(arkiv_node).build())
    account = NamedAccount.create("test-main-account")
    arkiv_node.fund_account(account)
    client = Arkiv(provider, account=account)
    
    original_account = client.eth.default_account
    original_signer = client.current_signer  # Track original account name
    assert original_signer is not None
    
    # Create and add second account
    second_account = NamedAccount.create("test-second-account")
    arkiv_node.fund_account(second_account)
    
    client.accounts["second-account"] = second_account
    
    # Verify account was added
    assert "second-account" in client.accounts
    assert client.accounts["second-account"].address == second_account.address
    
    # Switch to second account
    client.switch_to("second-account")
    assert client.eth.default_account == second_account.address
    assert client.current_signer == "second-account"
    
    # Create entity with second account
    entity_key, receipt = client.arkiv.create_entity(
        payload=b"Created by second account",
        content_type="text/plain",
        expires_in=3600
    )
    
    # Verify owner is second account
    entity = client.arkiv.get_entity(entity_key)
    assert entity is not None
    assert entity.owner == second_account.address
    
    # Switch back to original using tracked signer name
    client.switch_to(original_signer)
    assert client.eth.default_account == original_account
    assert client.current_signer == original_signer


def test_node_reference(arkiv_node):
    """Test accessing and using node reference."""
    # Use shared test node
    provider = cast(BaseProvider, ProviderBuilder().node(arkiv_node).build())
    account = NamedAccount.create("test-node-ref")
    arkiv_node.fund_account(account)
    client = Arkiv(provider, account=account)
    
    # Verify node properties via the shared node
    assert arkiv_node.http_url is not None
    assert arkiv_node.ws_url is not None
    assert "http://" in arkiv_node.http_url or "https://" in arkiv_node.http_url
    
    # Test funding via node
    test_account = NamedAccount.create("test-node-funding")
    arkiv_node.fund_account(test_account)
    
    balance = client.eth.get_balance(test_account.address)
    assert balance > 0


def test_accounts_registry(arkiv_node):
    """Test accounts registry functionality."""
    # Use shared test node
    provider = cast(BaseProvider, ProviderBuilder().node(arkiv_node).build())
    account = NamedAccount.create("test-registry-main")
    arkiv_node.fund_account(account)
    client = Arkiv(provider, account=account)
    
    # Client should have the account in registry
    assert len(client.accounts) > 0
    
    # Add multiple accounts
    account1 = NamedAccount.create("test-account-1")
    account2 = NamedAccount.create("test-account-2")
    
    arkiv_node.fund_account(account1)
    arkiv_node.fund_account(account2)
    
    client.accounts["account-1"] = account1
    client.accounts["account-2"] = account2
    
    # Verify registry
    assert "account-1" in client.accounts
    assert "account-2" in client.accounts
    assert client.accounts["account-1"].address == account1.address
    assert client.accounts["account-2"].address == account2.address
    
    # Test switching between accounts
    client.switch_to("account-1")
    assert client.eth.default_account == account1.address
    
    client.switch_to("account-2")
    assert client.eth.default_account == account2.address
