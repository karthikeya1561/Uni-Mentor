
import subprocess
import sys
import time
import os
import signal

def run_servers():
    # Paths
    project_root = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_root, 'frontend')

    print("🚀 Starting Uni Mentor Application...")

    # Start Flask Backend
    print("🔹 Starting Backend (Flask)...")
    backend_process = subprocess.Popen(
        [sys.executable, 'run.py'],
        cwd=project_root,
        shell=True
    )

    # Start Next.js Frontend
    print("🔹 Starting Frontend (Next.js)...")
    # Using npm run dev --prefix frontend to run from root
    frontend_cmd = 'npm run dev'
    frontend_process = subprocess.Popen(
        frontend_cmd,
        cwd=frontend_dir,
        shell=True
    )

    print("\n✅ Application is running!")
    print("   - Frontend: http://localhost:3000")
    print("   - Backend:  http://localhost:5000")
    print("\n(Press Ctrl+C to stop both servers)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        backend_process.terminate()
        # frontend_process.terminate() # shell=True makes this tricky on Windows, mainly relies on user closing window or complex tree kill
        if sys.platform == 'win32':
             subprocess.call(['taskkill', '/F', '/T', '/PID', str(backend_process.pid)])
             subprocess.call(['taskkill', '/F', '/T', '/PID', str(frontend_process.pid)])
        else:
            backend_process.kill()
            frontend_process.kill()
        
        print("✅ Servers stopped.")

if __name__ == "__main__":
    run_servers()
