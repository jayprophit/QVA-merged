"""
Blockchain Manager for QVA System.
Provides integration with blockchain networks and smart contract functionality.
"""

import os
import logging
import json
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger('QVA.Blockchain')

try:
    from web3 import Web3
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    logger.warning("Web3 not available. Blockchain functionality will be limited.")
    WEB3_AVAILABLE = False

class BlockchainManager:
    """
    Blockchain Manager for the QVA system.
    Handles blockchain integration and smart contract interactions.
    """
    
    def __init__(self, config):
        """
        Initialize the Blockchain Manager.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self._enabled = config.get('blockchain.enabled', False)
        self._node_url = config.get('blockchain.node', 'http://localhost:8545')
        self._smart_contract_address = config.get('blockchain.smart_contract_address', '0x0')
        self._contracts = {}
        self._web3 = None
        self._accounts = {}
        
        logger.info(f"Blockchain Manager initialized (enabled: {self._enabled})")
        
        # Initialize blockchain if enabled
        if self._enabled and WEB3_AVAILABLE:
            self._initialize_blockchain()
        
    def _initialize_blockchain(self):
        """Initialize the blockchain connection."""
        try:
            logger.info(f"Connecting to blockchain node: {self._node_url}")
            self._web3 = Web3(Web3.HTTPProvider(self._node_url))
            
            if not self._web3.is_connected():
                logger.warning(f"Failed to connect to blockchain node: {self._node_url}")
                self._enabled = False
                return
                
            logger.info(f"Connected to blockchain node. Network ID: {self._web3.net.version}")
            
            # Load contracts
            self._load_contracts()
            
        except Exception as e:
            logger.error(f"Error initializing blockchain: {e}", exc_info=True)
            self._enabled = False
            
    def _load_contracts(self):
        """Load smart contracts from configuration."""
        contracts_dir = os.path.join(os.path.dirname(__file__), 'contracts')
        
        if not os.path.exists(contracts_dir):
            os.makedirs(contracts_dir, exist_ok=True)
            logger.warning(f"Created contracts directory: {contracts_dir}")
            return
            
        for filename in os.listdir(contracts_dir):
            if filename.endswith('.json'):
                contract_path = os.path.join(contracts_dir, filename)
                contract_name = filename[:-5]  # Remove .json extension
                
                try:
                    with open(contract_path, 'r') as f:
                        contract_data = json.load(f)
                        
                    # Create contract instance
                    contract_address = contract_data.get('address')
                    contract_abi = contract_data.get('abi')
                    
                    if contract_address and contract_abi:
                        contract = self._web3.eth.contract(address=contract_address, abi=contract_abi)
                        self._contracts[contract_name] = contract
                        logger.debug(f"Loaded contract: {contract_name} at {contract_address}")
                    else:
                        logger.warning(f"Invalid contract data in {contract_path}")
                        
                except Exception as e:
                    logger.error(f"Error loading contract {contract_name}: {e}")
                    
        logger.info(f"Loaded {len(self._contracts)} contracts")
        
    def is_enabled(self) -> bool:
        """Check if blockchain functionality is enabled."""
        return self._enabled and WEB3_AVAILABLE
        
    def get_contract(self, contract_name: str):
        """Get a contract instance by name."""
        if not self.is_enabled():
            logger.warning("Blockchain functionality is not enabled")
            return None
            
        return self._contracts.get(contract_name)
        
    def create_account(self) -> Dict[str, Any]:
        """Create a new blockchain account."""
        if not self.is_enabled():
            logger.warning("Blockchain functionality is not enabled")
            return {}
            
        try:
            account = Account.create()
            account_id = account.address
            
            self._accounts[account_id] = {
                'address': account_id,
                'private_key': account.privateKey.hex(),
                'created_at': time.time()
            }
            
            return {
                'address': account_id
            }
            
        except Exception as e:
            logger.error(f"Error creating account: {e}")
            return {}
            
    def get_balance(self, address: str) -> float:
        """Get the balance of an address."""
        if not self.is_enabled():
            logger.warning("Blockchain functionality is not enabled")
            return 0.0
            
        try:
            balance_wei = self._web3.eth.get_balance(address)
            balance_eth = self._web3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
            
        except Exception as e:
            logger.error(f"Error getting balance for {address}: {e}")
            return 0.0
            
    def send_transaction(self, from_address: str, to_address: str, amount: float, private_key: Optional[str] = None) -> str:
        """Send a transaction from one address to another."""
        if not self.is_enabled():
            logger.warning("Blockchain functionality is not enabled")
            return ""
            
        try:
            # Convert amount to wei
            amount_wei = self._web3.to_wei(amount, 'ether')
            
            # Get nonce
            nonce = self._web3.eth.get_transaction_count(from_address)
            
            # Create transaction
            tx = {
                'nonce': nonce,
                'to': to_address,
                'value': amount_wei,
                'gas': 21000,
                'gasPrice': self._web3.eth.gas_price
            }
            
            # Sign transaction if private key is provided
            if private_key:
                signed_tx = self._web3.eth.account.sign_transaction(tx, private_key)
                tx_hash = self._web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            else:
                # If no private key, use default account
                tx_hash = self._web3.eth.send_transaction(tx)
                
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Error sending transaction: {e}")
            return ""
            
    def get_status(self) -> Dict[str, Any]:
        """Get the status of the blockchain manager."""
        return {
            'enabled': self._enabled,
            'web3_available': WEB3_AVAILABLE,
            'connected': self._web3.is_connected() if self._web3 else False,
            'node_url': self._node_url,
            'contracts': list(self._contracts.keys()),
            'accounts': len(self._accounts)
        } if self.is_enabled() else {
            'enabled': False,
            'web3_available': WEB3_AVAILABLE
        }