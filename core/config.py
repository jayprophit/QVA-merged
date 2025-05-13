"""
Configuration management for the QVA system.
Handles loading, validation, and access to configuration parameters.
"""

import os
import json
import logging
from typing import Any, Dict, Optional, Union
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger('QVA.Config')

class ConfigManager:
    """
    Configuration manager for the QVA system.
    Handles loading from environment variables, JSON files, and defaults.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to JSON configuration file (optional)
        """
        # Load environment variables
        load_dotenv()
        
        self._config = {}
        self._config_path = config_path
        
        # Load configuration
        self._load_defaults()
        
        if config_path:
            self._load_config_file(config_path)
            
        self._load_environment_vars()
        
        logger.debug("Configuration initialized")
    
    def _load_defaults(self) -> None:
        """Load default configuration values."""
        self._config = {
            # System settings
            'system': {
                'mode': 'server',
                'debug': False,
                'log_level': 'info',
                'port': 8000,
                'host': '0.0.0.0',
            },
            
            # Database settings
            'database': {
                'url': 'sqlite:///qva.db',
                'pool_size': 10,
                'max_overflow': 20,
            },
            
            # Security settings
            'security': {
                'secret_key': os.urandom(24).hex(),
                'token_expiry': 86400,  # 24 hours in seconds
                'enable_2fa': False,
            },
            
            # AI settings
            'ai': {
                'model_path': './models',
                'openai_api_key': '',
                'enable_local_ai': True,
                'model_type': 'gpt-4',
            },
            
            # Quantum settings
            'quantum': {
                'enable_simulation': True,
                'cores': 4,
                'memory': 4096,
            },
            
            # Blockchain settings
            'blockchain': {
                'enabled': False,
                'node': 'http://localhost:8545',
                'smart_contract_address': '0x0',
            },
            
            # Frontend settings
            'frontend': {
                'url': 'http://localhost:3000',
                'enable_3d_ui': True,
                'enable_voice_interface': True,
            },
            
            # API settings
            'api': {
                'enable_external': False,
                'rate_limit': 100,
            },
            
            # Components configuration
            'components': {}
        }
    
    def _load_config_file(self, config_path: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the JSON configuration file
        """
        try:
            path = Path(config_path)
            if not path.exists():
                logger.warning(f"Configuration file not found: {config_path}")
                return
                
            with open(path, 'r') as f:
                file_config = json.load(f)
                
            # Update configuration with file values
            self._update_config(file_config)
            logger.info(f"Loaded configuration from {config_path}")
                
        except Exception as e:
            logger.error(f"Failed to load configuration file: {e}")
    
    def _load_environment_vars(self) -> None:
        """Load configuration from environment variables."""
        # System settings
        self._update_from_env('system.mode', 'QVA_MODE')
        self._update_from_env('system.debug', 'QVA_DEBUG', is_bool=True)
        self._update_from_env('system.log_level', 'QVA_LOG_LEVEL')
        self._update_from_env('system.port', 'QVA_PORT', is_int=True)
        self._update_from_env('system.host', 'QVA_HOST')
        
        # Database settings
        self._update_from_env('database.url', 'DATABASE_URL')
        self._update_from_env('database.pool_size', 'DATABASE_POOL_SIZE', is_int=True)
        self._update_from_env('database.max_overflow', 'DATABASE_MAX_OVERFLOW', is_int=True)
        
        # Security settings
        self._update_from_env('security.secret_key', 'SECRET_KEY')
        self._update_from_env('security.token_expiry', 'TOKEN_EXPIRY', is_int=True)
        self._update_from_env('security.enable_2fa', 'ENABLE_2FA', is_bool=True)
        
        # AI settings
        self._update_from_env('ai.model_path', 'AI_MODEL_PATH')
        self._update_from_env('ai.openai_api_key', 'OPENAI_API_KEY')
        self._update_from_env('ai.enable_local_ai', 'ENABLE_LOCAL_AI', is_bool=True)
        self._update_from_env('ai.model_type', 'AI_MODEL_TYPE')
        
        # Quantum settings
        self._update_from_env('quantum.enable_simulation', 'ENABLE_QUANTUM_SIMULATION', is_bool=True)
        self._update_from_env('quantum.cores', 'QUANTUM_CORES', is_int=True)
        self._update_from_env('quantum.memory', 'QUANTUM_MEMORY', is_int=True)
        
        # Blockchain settings
        self._update_from_env('blockchain.enabled', 'BLOCKCHAIN_ENABLED', is_bool=True)
        self._update_from_env('blockchain.node', 'BLOCKCHAIN_NODE')
        self._update_from_env('blockchain.smart_contract_address', 'SMART_CONTRACT_ADDRESS')
        
        # Frontend settings
        self._update_from_env('frontend.url', 'FRONTEND_URL')
        self._update_from_env('frontend.enable_3d_ui', 'ENABLE_3D_UI', is_bool=True)
        self._update_from_env('frontend.enable_voice_interface', 'ENABLE_VOICE_INTERFACE', is_bool=True)
        
        # API settings
        self._update_from_env('api.enable_external', 'ENABLE_EXTERNAL_API', is_bool=True)
        self._update_from_env('api.rate_limit', 'API_RATE_LIMIT', is_int=True)
    
    def _update_from_env(self, config_key: str, env_var: str, is_bool: bool = False, is_int: bool = False) -> None:
        """
        Update a configuration value from an environment variable.
        
        Args:
            config_key: The configuration key (dot notation)
            env_var: The environment variable name
            is_bool: Whether the value should be converted to a boolean
            is_int: Whether the value should be converted to an integer
        """
        if env_var in os.environ:
            value = os.environ[env_var]
            
            if is_bool:
                value = value.lower() in ('true', 'yes', '1', 'y')
            elif is_int:
                try:
                    value = int(value)
                except ValueError:
                    logger.warning(f"Could not convert {env_var}={value} to integer")
                    return
                    
            self.set(config_key, value)
    
    def _update_config(self, update_dict: Dict[str, Any], base_dict: Optional[Dict[str, Any]] = None, prefix: str = '') -> None:
        """
        Recursively update configuration dictionary.
        
        Args:
            update_dict: Dictionary with values to update
            base_dict: Base dictionary to update (default: self._config)
            prefix: Prefix for keys (used for recursion)
        """
        if base_dict is None:
            base_dict = self._config
            
        for key, value in update_dict.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                # Create the key if it doesn't exist
                if key not in base_dict:
                    base_dict[key] = {}
                    
                # Recursively update nested dictionary
                self._update_config(value, base_dict[key], full_key)
            else:
                # Update value directly
                base_dict[key] = value
                logger.debug(f"Updated config: {full_key} = {value}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key (dot notation)
            default: Default value if key doesn't exist
            
        Returns:
            The configuration value or default
        """
        parts = key.split('.')
        current = self._config
        
        for part in parts:
            if part not in current:
                return default
                
            current = current[part]
            
        return current
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: The configuration key (dot notation)
            value: The value to set
        """
        parts = key.split('.')
        current = self._config
        
        # Navigate to the parent of the target key
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
                
            current = current[part]
            
        # Set the value
        current[parts[-1]] = value
        logger.debug(f"Set config: {key} = {value}")
    
    def save(self, path: Optional[str] = None) -> None:
        """
        Save the current configuration to a JSON file.
        
        Args:
            path: Path to save the configuration file (default: self._config_path)
        """
        save_path = path or self._config_path
        
        if not save_path:
            logger.warning("No path specified for saving configuration")
            return
            
        try:
            with open(save_path, 'w') as f:
                json.dump(self._config, f, indent=2)
                
            logger.info(f"Saved configuration to {save_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get the entire configuration dictionary.
        
        Returns:
            The complete configuration dictionary
        """
        return self._config
