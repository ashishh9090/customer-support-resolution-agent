import os
import sys
import subprocess
import signal
import time

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VENV_PYTHON = os.path.join(ROOT_DIR, "venv/bin/python")
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable


def run_dev():
    print("=" * 65)
    print("🚀 Starting AI Customer Support Resolution Agent (Dev Mode)")
    print("=" * 65)
    print("Backend API:  http://localhost:8000")
    print("API Docs:     http://localhost:8000/api/v1/docs")
    print("Frontend UI:  http://localhost:5173")
    print("=" * 65)

    backend_env = os.environ.copy()
    backend_env["PYTHONPATH"] = ROOT_DIR

    backend_proc = subprocess.Popen(
        [VENV_PYTHON, "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=ROOT_DIR,
        env=backend_env,
    )

    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"],
        cwd=os.path.join(ROOT_DIR, "frontend"),
    )

    def signal_handler(sig, frame):
        print("\n🛑 Shutting down development servers...")
        try:
            backend_proc.terminate()
            frontend_proc.terminate()
            backend_proc.wait(timeout=3)
            frontend_proc.wait(timeout=3)
        except Exception:
            backend_proc.kill()
            frontend_proc.kill()
        print("Dev servers cleanly stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    run_dev()
