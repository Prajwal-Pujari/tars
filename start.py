import subprocess
import time
import sys
import signal

def start_services():
    import os
    os.makedirs("logs", exist_ok=True)
    
    print("[System] Cleaning up old background processes...")
    try:
        subprocess.run(["pkill", "-f", "python main.py"], check=False, capture_output=True)
        subprocess.run(["pkill", "-f", "python dashboard.py"], check=False, capture_output=True)
        time.sleep(1) # Give OS a second to free the ports
    except Exception:
        pass
        
    api_log = open("logs/api.log", "w")
    dash_log = open("logs/dashboard.log", "w")
    
    print("[System] Starting TARS API Server...")
    api_process = subprocess.Popen([sys.executable, "main.py"], stdout=api_log, stderr=subprocess.STDOUT)
    
    print("[System] Starting TARS Dashboard Server...")
    dashboard_process = subprocess.Popen([sys.executable, "dashboard.py"], stdout=dash_log, stderr=subprocess.STDOUT)
    
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
        # Add a quick health check to make sure the NEW server actually booted!
        try:
            import requests
            requests.get("http://127.0.0.1:8000/health", timeout=3)
        except Exception:
            print("[bold red]CRITICAL ERROR: API Server failed to boot! Check logs/api.log for the python traceback.[/bold red]")
            cleanup()
            return
            
        cli.main()
        
    except Exception as e:
        print(f"[System] Error starting TARS: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
