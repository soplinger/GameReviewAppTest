#!/usr/bin/env python3
"""
Startup script for the Game Review Backend API
"""
import sys
import os

# Get the directory where this script is located (backend/)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change to the backend directory
os.chdir(script_dir)

# Add the current directory to Python path
sys.path.insert(0, script_dir)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)