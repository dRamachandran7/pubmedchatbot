#!/usr/bin/env python3
"""
RAG Service runner - use this to start the service with:
  python run.py
"""
import sys
import os

# Add parent directory to path so relative imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
