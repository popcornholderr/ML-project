import sys
import socket
import uvicorn

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

if __name__ == "__main__":
    port = 8000
    if is_port_in_use(8000):
        port = 8001

    print("\n" + "="*60)
    print("  PREDICT YOUR PLACEMENT — LIQUID GLASS WEB PLATFORM")
    print("="*60)
    print(f"  Serving Frontend & API at: http://localhost:{port}")
    print(f"  Interactive API Docs at:   http://localhost:{port}/docs")
    print("="*60 + "\n")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=port, reload=True)
