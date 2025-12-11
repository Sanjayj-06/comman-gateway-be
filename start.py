#!/usr/bin/env python
"""
Start the Command Gateway server.
Use --reload for development (watches for file changes)
"""
import uvicorn
import sys

if __name__ == "__main__":
    
    reload = "--reload" in sys.argv
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=reload,
        reload_excludes=["*.db", "*.sqlite*", "__pycache__", "*.pyc"] if reload else None
    )
