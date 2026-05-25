import subprocess
import time
import sys
import signal

def start_services():
    print("[System] Starting TARS API Server...")
    api_process = subprocess.Popen([sys.executable, "main.py"])
    
    print("[System] Starting TARS Dashboard Server...")
    dashboard_process = subprocess.Popen([sys.executable, "dashboard.py"])
    
    print("[System] Waiting for servers to initialize (this may take a few seconds)...")
    time.sleep(5) # Give the FastApi and Uvicorn servers time to bind to ports
    
    return api_process, dashboard_process

def main():
    api_process = None
    dashboard_process = None
    
    def cleanup(signum=None, frame=None):
        print("\n[System] Shutting down TARS services...")
        if api_process and api_process.poll() is None:
            api_process.terminate()
        if dashboard_process and dashboard_process.poll() is None:
            dashboard_process.terminate()
        sys.exit(0)
        
    # Catch Ctrl+C and termination signals to cleanly kill the background servers
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    try:
        api_process, dashboard_process = start_services()
        
        print("\n[System] Services are running in the background.")
        print("[System] API accessible remotely at: http://<UBUNTU_IP>:8000")
        print("[System] Dashboard accessible remotely at: http://<UBUNTU_IP>:8888")
        print("\n========================================================\n")
        
        # Start the CLI interface right here in the same terminal
        import cli
        cli.main()
        
    except Exception as e:
        print(f"[System] Error starting TARS: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
