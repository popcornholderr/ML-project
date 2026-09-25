import os
import socket
import uvicorn


def is_port_in_use(port: int) -> bool:
    """Check whether a local port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


if __name__ == "__main__":
    # Render provides the PORT environment variable.
    # Locally, use 8000 and fall back to 8001 if needed.
    port = int(os.environ.get("PORT", 8000))

    # Render requires binding to 0.0.0.0.
    host = "0.0.0.0" if "PORT" in os.environ else "127.0.0.1"

    if "PORT" not in os.environ and is_port_in_use(port):
        port = 8001

    print("\n" + "=" * 60)
    print("  PREDICT YOUR PLACEMENT — LIQUID GLASS WEB PLATFORM")
    print("=" * 60)
    print(f"  Serving Frontend & API at: http://{host}:{port}")
    print(f"  Interactive API Docs at:   http://{host}:{port}/docs")
    print("=" * 60 + "\n")

    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=("PORT" not in os.environ),
    )
