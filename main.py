#!/usr/bin/env python3
"""
Quantum Virtual Assistant (QVA) - Main System Entry Point
Integrates multiple AI, quantum, and virtual assistant technologies into a unified system.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=os.getenv('QVA_LOG_LEVEL', 'INFO').upper(),
    format=log_format,
    handlers=[
        logging.FileHandler(f"logs/qva_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('QVA')

# Import core components
try:
    # Create necessary directories if they don't exist
    os.makedirs('logs', exist_ok=True)
    
    # Import system components
    from core.system import QVASystem
    from core.config import ConfigManager
    from core.quantum import QuantumProcessor
    from core.ai import AIOrchestrator
    from core.interfaces import InterfaceManager
    
    logger.info("QVA core modules loaded successfully")
except ImportError as e:
    logger.critical(f"Failed to import core modules: {e}")
    logger.critical("Please ensure all dependencies are installed by running: pip install -r requirements.txt")
    sys.exit(1)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Quantum Virtual Assistant (QVA)')
    parser.add_argument('--mode', choices=['server', 'cli', 'desktop', 'service'], 
                        default=os.getenv('QVA_MODE', 'server'),
                        help='Operation mode for QVA')
    parser.add_argument('--config', type=str, 
                        default=os.getenv('QVA_CONFIG', 'config/default.json'),
                        help='Path to configuration file')
    parser.add_argument('--debug', action='store_true', 
                        default=os.getenv('QVA_DEBUG', 'false').lower() == 'true',
                        help='Enable debug mode')
    return parser.parse_args()

def main():
    """Main entry point for the QVA system."""
    args = parse_arguments()
    
    logger.info(f"Starting QVA System in {args.mode} mode")
    logger.debug(f"Debug mode: {args.debug}")
    
    try:
        # Initialize configuration
        config_manager = ConfigManager(args.config)
        
        # Initialize core system components
        quantum_processor = QuantumProcessor(config_manager)
        ai_orchestrator = AIOrchestrator(config_manager)
        interface_manager = InterfaceManager(config_manager)
        
        # Create and start the main system
        system = QVASystem(
            config=config_manager,
            quantum=quantum_processor,
            ai=ai_orchestrator,
            interfaces=interface_manager,
            mode=args.mode,
            debug=args.debug
        )
        
        # Start the system
        system.start()
        
    except Exception as e:
        logger.critical(f"Failed to start QVA system: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("QVA system shutdown complete")

if __name__ == "__main__":
    main()
