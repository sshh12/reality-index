#!/usr/bin/env python3
"""
Development server startup script
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    from backend.api import app
    
    print("🌐 Starting development server...")
    print("   API will be available at: http://localhost:8080/api/")
    print("   Health check: http://localhost:8080/health")
    print("   Admin stats: http://localhost:8080/api/admin/stats")
    
    uvicorn.run("backend.api:app", host="0.0.0.0", port=8080, reload=True)