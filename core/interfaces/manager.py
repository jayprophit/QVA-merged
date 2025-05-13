"""
Interface Manager for QVA System.
Manages user interfaces and coordinations between them.
"""

import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger('QVA.Interfaces')

class InterfaceManager:
    """
    Interface Manager for the QVA system.
    Handles multiple UI interfaces including web, desktop, and holographic.
    """
    
    def __init__(self, config):
        """
        Initialize the Interface Manager.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self._interfaces = {}
        self._initialized = False
        
        # Load configuration
        self._frontend_url = config.get('frontend.url', 'http://localhost:3000')
        self._enable_3d_ui = config.get('frontend.enable_3d_ui', True)
        self._enable_voice = config.get('frontend.enable_voice_interface', True)
        
        logger.info(f"Interface Manager initialized")
        
    def initialize(self):
        """Initialize interfaces."""
        if self._initialized:
            logger.warning("Interfaces already initialized")
            return
            
        logger.info("Initializing interfaces")
        
        # Initialize web interface
        self._init_web_interface()
        
        # Initialize desktop interface if enabled
        if self.config.get('frontend.enable_desktop', False):
            self._init_desktop_interface()
            
        # Initialize mobile interface if enabled
        if self.config.get('frontend.enable_mobile', False):
            self._init_mobile_interface()
            
        # Initialize holographic interface if enabled
        if self._enable_3d_ui:
            self._init_holographic_interface()
            
        # Initialize voice interface if enabled
        if self._enable_voice:
            self._init_voice_interface()
            
        self._initialized = True
        logger.info(f"Initialized {len(self._interfaces)} interfaces")
        
    def _init_web_interface(self):
        """Initialize the web interface."""
        logger.info("Initializing web interface")
        
        self._interfaces['web'] = {
            'type': 'web',
            'url': self._frontend_url,
            'enabled': True,
            'status': 'initialized'
        }
        
    def _init_desktop_interface(self):
        """Initialize the desktop interface."""
        logger.info("Initializing desktop interface")
        
        self._interfaces['desktop'] = {
            'type': 'desktop',
            'enabled': True,
            'status': 'initialized'
        }
        
    def _init_mobile_interface(self):
        """Initialize the mobile interface."""
        logger.info("Initializing mobile interface")
        
        self._interfaces['mobile'] = {
            'type': 'mobile',
            'enabled': True,
            'status': 'initialized'
        }
        
    def _init_holographic_interface(self):
        """Initialize the holographic/3D interface."""
        logger.info("Initializing holographic interface")
        
        self._interfaces['holographic'] = {
            'type': 'holographic',
            'enabled': self._enable_3d_ui,
            'status': 'initialized'
        }
        
    def _init_voice_interface(self):
        """Initialize the voice interface."""
        logger.info("Initializing voice interface")
        
        self._interfaces['voice'] = {
            'type': 'voice',
            'enabled': self._enable_voice,
            'status': 'initialized'
        }
        
    def get_status(self) -> Dict[str, Any]:
        """Get the status of the interface manager."""
        return {
            'initialized': self._initialized,
            'interfaces': len(self._interfaces),
            'web_url': self._frontend_url,
            'enable_3d_ui': self._enable_3d_ui,
            'enable_voice': self._enable_voice
        }