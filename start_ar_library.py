#!/usr/bin/env python3
"""
AR Library Startup Script
This script helps you set up and run the AR Library system
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🚀 AR LIBRARY SYSTEM")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_postgres():
    """Check if PostgreSQL is running"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='Post',
            host='localhost',
            port='5432'
        )
        conn.close()
        print("✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("💡 Make sure PostgreSQL is running and credentials are correct")
        return False

def setup_database():
    """Set up the AR library database"""
    print("\n📊 Setting up database...")
    try:
        result = subprocess.run([
            sys.executable, "backend/setup_ar_database.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ Database setup completed")
            return True
        else:
            print(f"❌ Database setup failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running database setup: {e}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Python dependencies installed")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def install_frontend_dependencies():
    """Install frontend dependencies"""
    print("\n📦 Installing frontend dependencies...")
    try:
        result = subprocess.run([
            "npm", "install"
        ], capture_output=True, text=True, cwd="frontend")
        
        if result.returncode == 0:
            print("✅ Frontend dependencies installed")
            return True
        else:
            print(f"❌ Failed to install frontend dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing frontend dependencies: {e}")
        return False

def start_backend():
    """Start the FastAPI backend"""
    print("\n🔧 Starting backend server...")
    try:
        # Start backend in background
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], cwd="backend")
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server started successfully")
                return backend_process
        except:
            pass
        
        print("✅ Backend server starting...")
        return backend_process
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the React frontend"""
    print("\n🌐 Starting frontend server...")
    try:
        # Start frontend in background
        frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd="frontend")
        
        # Wait a moment for server to start
        time.sleep(5)
        
        print("✅ Frontend server starting...")
        return frontend_process
        
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def main():
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        return
    
    if not check_postgres():
        print("\n💡 Please start PostgreSQL and try again")
        return
    
    # Setup
    if not setup_database():
        print("\n❌ Database setup failed. Please check PostgreSQL configuration.")
        return
    
    if not install_dependencies():
        print("\n❌ Failed to install Python dependencies")
        return
    
    if not install_frontend_dependencies():
        print("\n❌ Failed to install frontend dependencies")
        return
    
    # Start servers
    print("\n🚀 Starting AR Library system...")
    
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend")
        return
    
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend")
        backend_process.terminate()
        return
    
    print("\n" + "=" * 60)
    print("🎉 AR LIBRARY SYSTEM IS RUNNING!")
    print("=" * 60)
    print("📱 Frontend: http://localhost:5173")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 Admin Dashboard: http://localhost:5173/admin")
    print("🔍 Public Scanner: http://localhost:5173/scanner")
    print("\n💡 Press Ctrl+C to stop all servers")
    print("=" * 60)
    
    # Open browser
    try:
        webbrowser.open("http://localhost:5173")
    except:
        pass
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping servers...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()
