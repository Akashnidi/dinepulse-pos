"""
Entry point – run with: uv run python main.py
Or after packaging: pos_server.exe
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="warning",
    )
