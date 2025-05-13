"""
API Server for QVA System.
Provides REST API endpoints and serves the web interface.
"""

import os
import json
import logging
import threading
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger('QVA.API')

try:
    from fastapi import FastAPI, HTTPException, Depends, Request, Response
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("FastAPI or uvicorn not available. API server will not be fully functional.")
    FASTAPI_AVAILABLE = False

class APIServer:
    """
    API Server for the QVA system.
    Provides REST API endpoints using FastAPI.
    """
    
    def __init__(self, system, host="0.0.0.0", port=8000):
        """
        Initialize the API server.
        
        Args:
            system: QVA system instance
            host: Host to bind the server to
            port: Port to bind the server to
        """
        self.system = system
        self.host = host
        self.port = port
        self._app = None
        self._running = False
        self._thread = None
        
        # Routes and endpoints
        self._routes = {}
        
        # Initialize the API server if FastAPI is available
        if FASTAPI_AVAILABLE:
            self._init_api()
        
    def _init_api(self):
        """Initialize the FastAPI application."""
        app = FastAPI(title="QVA API", description="Quantum Virtual Assistant API", version="1.0.0")
        
        # Configure CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, restrict this to known origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self._register_routes(app)
        
        # Serve static files if available
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend/web")
        if os.path.exists(frontend_dir):
            app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
        
        self._app = app
        
    def _register_routes(self, app):
        """Register API routes."""
        # System status endpoint
        @app.get("/api/status")
        def get_status():
            return self.system.get_status()
        
        # Quantum endpoints
        @app.get("/api/quantum/status")
        def get_quantum_status():
            return self.system.quantum.get_status()
        
        # AI endpoints
        @app.get("/api/ai/status")
        def get_ai_status():
            return self.system.ai.get_status()
            
        @app.get("/api/ai/agents")
        def list_agents():
            return self.system.ai.list_agents()
        
        # Create more endpoints as needed
        
    def run(self):
        """Run the API server."""
        if not FASTAPI_AVAILABLE:
            logger.error("Cannot run API server: FastAPI or uvicorn not available.")
            return
            
        if self._running:
            logger.warning("API server is already running")
            return
            
        logger.info(f"Starting API server on {self.host}:{self.port}")
        self._running = True
        
        # Run the server using uvicorn
        try:
            uvicorn.run(self._app, host=self.host, port=self.port)
        except Exception as e:
            logger.error(f"Error running API server: {e}", exc_info=True)
            self._running = False
            
    def run_async(self):
        """Run the API server in a separate thread."""
        if not FASTAPI_AVAILABLE:
            logger.error("Cannot run API server: FastAPI or uvicorn not available.")
            return
            
        if self._running:
            logger.warning("API server is already running")
            return
            
        logger.info(f"Starting API server on {self.host}:{self.port} in background")
        
        # Start the server in a new thread
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()
        
    def stop(self):
        """Stop the API server."""
        if not self._running:
            logger.warning("API server is not running")
            return
            
        logger.info("Stopping API server")
        self._running = False
        
        # The uvicorn server is stopped when the thread is terminated

def create_api_server(system, host=None, port=None):
    """
    Create an API server for the QVA system.
    
    Args:
        system: QVA system instance
        host: Host to bind the server to (default: from system config)
        port: Port to bind the server to (default: from system config)
        
    Returns:
        APIServer instance
    """
    if not host:
        host = system.config.get('system.host', '0.0.0.0')
        
    if not port:
        port = system.config.get('system.port', 8000)
        
    return APIServer(system, host, port)