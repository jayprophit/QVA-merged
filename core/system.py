"""
QVA System - Core orchestration system that integrates all QVA components.
Merges functionality from QVA, QVA-v1, VM-VA-MAIA-QC, and QuantumVirtualAssistant repositories.
"""

import os
import sys
import time
import logging
import threading
import signal
from typing import Dict, Any, Optional, List

logger = logging.getLogger('QVA.System')

class QVASystem:
    """Main system class that orchestrates all QVA components."""
    
    def __init__(self, config, quantum, ai, interfaces, mode='server', debug=False):
        """
        Initialize the QVA System.
        
        Args:
            config: Configuration manager
            quantum: Quantum processor instance
            ai: AI orchestrator instance
            interfaces: Interface manager
            mode: Operation mode (server, cli, desktop, service)
            debug: Enable debug mode
        """
        self.config = config
        self.quantum = quantum
        self.ai = ai
        self.interfaces = interfaces
        self.mode = mode
        self.debug = debug
        
        self._running = False
        self._threads = []
        self._components = {}
        self._subsystems = {}
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"QVA System initialized in {mode} mode")
        
    def register_component(self, name: str, component: Any) -> None:
        """Register a component with the system."""
        self._components[name] = component
        logger.debug(f"Registered component: {name}")
        
    def register_subsystem(self, name: str, subsystem: Any) -> None:
        """Register a subsystem with the system."""
        self._subsystems[name] = subsystem
        logger.debug(f"Registered subsystem: {name}")
        
    def start(self) -> None:
        """Start the QVA system and all its components."""
        if self._running:
            logger.warning("System is already running")
            return
            
        logger.info("Starting QVA System")
        self._running = True
        
        try:
            # Initialize and start components
            self._init_components()
            
            # Start mode-specific operation
            if self.mode == 'server':
                self._start_server_mode()
            elif self.mode == 'cli':
                self._start_cli_mode()
            elif self.mode == 'desktop':
                self._start_desktop_mode()
            elif self.mode == 'service':
                self._start_service_mode()
            else:
                logger.error(f"Unknown mode: {self.mode}")
                self.stop()
                return
                
            # Main loop - keep running until stopped
            while self._running:
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error during system operation: {e}", exc_info=True)
            self.stop()
            
    def stop(self) -> None:
        """Stop the QVA system and all its components."""
        if not self._running:
            logger.warning("System is not running")
            return
            
        logger.info("Stopping QVA System")
        self._running = False
        
        # Stop all components
        for name, component in self._components.items():
            try:
                if hasattr(component, 'stop'):
                    logger.debug(f"Stopping component: {name}")
                    component.stop()
            except Exception as e:
                logger.error(f"Error stopping component {name}: {e}")
                
        # Stop all subsystems
        for name, subsystem in self._subsystems.items():
            try:
                if hasattr(subsystem, 'stop'):
                    logger.debug(f"Stopping subsystem: {name}")
                    subsystem.stop()
            except Exception as e:
                logger.error(f"Error stopping subsystem {name}: {e}")
                
        # Join all threads
        for thread in self._threads:
            if thread.is_alive():
                thread.join(timeout=5.0)
                
        logger.info("QVA System stopped")
        
    def _init_components(self) -> None:
        """Initialize all system components."""
        logger.debug("Initializing system components")
        
        # Start the quantum processor
        self.quantum.start()
        
        # Start the AI orchestrator
        self.ai.start()
        
        # Initialize interfaces
        self.interfaces.initialize()
        
        # Load additional components based on configuration
        self._load_additional_components()
        
    def _load_additional_components(self) -> None:
        """Load additional components based on configuration."""
        components_config = self.config.get('components', {})
        
        for component_name, component_config in components_config.items():
            if not component_config.get('enabled', True):
                continue
                
            try:
                # Dynamically import and initialize component
                module_path = component_config.get('module')
                class_name = component_config.get('class')
                
                if not module_path or not class_name:
                    logger.warning(f"Missing module or class for component {component_name}")
                    continue
                    
                module = __import__(module_path, fromlist=[class_name])
                component_class = getattr(module, class_name)
                
                # Initialize component with config
                component = component_class(self.config)
                
                # Register component
                self.register_component(component_name, component)
                
                # Start component if it has a start method
                if hasattr(component, 'start'):
                    component.start()
                    
            except Exception as e:
                logger.error(f"Error loading component {component_name}: {e}", exc_info=True)
        
    def _start_server_mode(self) -> None:
        """Start the system in server mode."""
        from backend.api import create_api_server
        
        logger.info("Starting in server mode")
        server = create_api_server(self)
        server_thread = threading.Thread(target=server.run, daemon=True)
        server_thread.start()
        self._threads.append(server_thread)
        
    def _start_cli_mode(self) -> None:
        """Start the system in CLI mode."""
        from core.interfaces.cli import QVACLI
        
        logger.info("Starting in CLI mode")
        cli = QVACLI(self)
        cli_thread = threading.Thread(target=cli.run, daemon=True)
        cli_thread.start()
        self._threads.append(cli_thread)
        
    def _start_desktop_mode(self) -> None:
        """Start the system in desktop application mode."""
        from frontend.desktop import create_desktop_app
        
        logger.info("Starting in desktop mode")
        app = create_desktop_app(self)
        # Desktop UI typically runs in the main thread
        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()
        self._threads.append(app_thread)
        
    def _start_service_mode(self) -> None:
        """Start the system in background service mode."""
        logger.info("Starting in service mode")
        # Service mode runs with minimal UI, focusing on background processing
        
    def _signal_handler(self, signum, frame) -> None:
        """Handle termination signals for graceful shutdown."""
        logger.info(f"Received signal {signum}, shutting down")
        self.stop()
        
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the system."""
        return {
            'running': self._running,
            'mode': self.mode,
            'components': {name: self._get_component_status(comp) for name, comp in self._components.items()},
            'quantum_status': self.quantum.get_status(),
            'ai_status': self.ai.get_status(),
            'interfaces': self.interfaces.get_status()
        }
        
    def _get_component_status(self, component: Any) -> Dict[str, Any]:
        """Get the status of a component."""
        if hasattr(component, 'get_status'):
            return component.get_status()
        elif hasattr(component, 'status'):
            return component.status
        else:
            return {'status': 'unknown'}
