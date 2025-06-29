#!/usr/bin/env python3
"""
Ollama Server Starter Script
Starts Ollama server with proper configuration for HTTP endpoint usage
"""

import os
import sys
import time
import subprocess
import platform
import signal
import atexit
from pathlib import Path


class OllamaServer:
    def __init__(self, host="127.0.0.1", port="11434"):
        self.host = host
        self.port = port
        self.process = None
        self.endpoint = f"http://{host}:{port}"
        
    def start(self):
        """Start Ollama server with proper configuration."""
        print(f"🚀 Starting Ollama server on {self.endpoint}")
        
        # Set environment variables
        env = os.environ.copy()
        env["OLLAMA_ORIGINS"] = "*"
        env["OLLAMA_HOST"] = f"{self.host}:{self.port}"
        
        try:
            # Check if Ollama is installed
            subprocess.run(["ollama", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Ollama is not installed. Please install it first:")
            print("   curl -fsSL https://ollama.ai/install.sh | sh")
            sys.exit(1)
        
        # Start Ollama server
        try:
            if platform.system() == "Windows":
                # Windows: Start process in background
                self.process = subprocess.Popen(
                    ["ollama", "serve"],
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                # Unix/macOS: Start process in background
                self.process = subprocess.Popen(
                    ["ollama", "serve"],
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    preexec_fn=os.setsid
                )
            
            # Wait for server to start
            self._wait_for_server()
            print(f"✅ Ollama server started successfully on {self.endpoint}")
            print(f"   Process ID: {self.process.pid}")
            
            # Register cleanup function
            atexit.register(self.stop)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start Ollama server: {e}")
            return False
    
    def _wait_for_server(self, timeout=30):
        """Wait for server to be ready."""
        import requests
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.endpoint}/api/tags", timeout=2)
                if response.status_code == 200:
                    return True
            except:
                pass
            time.sleep(1)
        
        raise TimeoutError("Ollama server failed to start within timeout")
    
    def stop(self):
        """Stop Ollama server."""
        if self.process:
            print(f"🛑 Stopping Ollama server (PID: {self.process.pid})")
            try:
                if platform.system() == "Windows":
                    self.process.terminate()
                else:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                
                # Wait for process to terminate
                self.process.wait(timeout=10)
                print("✅ Ollama server stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing Ollama server")
                if platform.system() == "Windows":
                    self.process.kill()
                else:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
            except Exception as e:
                print(f"⚠️  Error stopping server: {e}")
            finally:
                self.process = None
    
    def is_running(self):
        """Check if server is running."""
        if not self.process:
            return False
        
        try:
            self.process.poll()
            return self.process.returncode is None
        except:
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Start Ollama server for code review")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", default="11434", help="Port to bind to (default: 11434)")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (background)")
    parser.add_argument("--pid-file", help="Write PID to file")
    
    args = parser.parse_args()
    
    server = OllamaServer(args.host, args.port)
    
    if args.pid_file:
        # Write PID to file
        with open(args.pid_file, 'w') as f:
            f.write(str(os.getpid()))
    
    if args.daemon:
        # Run in background
        if server.start():
            print(f"Ollama server running in background on {server.endpoint}")
            print(f"To stop: kill {server.process.pid}")
        else:
            sys.exit(1)
    else:
        # Run in foreground
        try:
            if server.start():
                print(f"Ollama server running on {server.endpoint}")
                print("Press Ctrl+C to stop")
                
                # Keep running
                while server.is_running():
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
        finally:
            server.stop()


if __name__ == "__main__":
    main() 