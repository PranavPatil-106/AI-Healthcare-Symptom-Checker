#!/usr/bin/env python3
"""
Convenience script to run both the backend and frontend simultaneously.
"""

import subprocess
import sys
import time
import threading
import os

def run_backend():
    """Run the FastAPI backend server."""
    print("Starting FastAPI backend...")
    try:
        # Change to backend directory
        os.chdir("backend")
        # Run the backend
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\nBackend stopped.")
    except Exception as e:
        print(f"Error running backend: {e}")

def run_frontend():
    """Run the Streamlit frontend."""
    print("Starting Streamlit frontend...")
    try:
        # Wait a moment for backend to start
        time.sleep(2)
        # Change to frontend directory
        os.chdir("../frontend")
        # Run the frontend
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\nFrontend stopped.")
    except Exception as e:
        print(f"Error running frontend: {e}")

def main():
    """Main function to run both backend and frontend."""
    print("Healthcare Symptom Checker - Starting both backend and frontend...")
    print("Press Ctrl+C to stop both servers.")
    
    # Create threads for backend and frontend
    backend_thread = threading.Thread(target=run_backend)
    frontend_thread = threading.Thread(target=run_frontend)
    
    # Start both threads
    backend_thread.start()
    frontend_thread.start()
    
    try:
        # Wait for both threads to complete
        backend_thread.join()
        frontend_thread.join()
    except KeyboardInterrupt:
        print("\nShutting down both servers...")
        sys.exit(0)

if __name__ == "__main__":
    main()