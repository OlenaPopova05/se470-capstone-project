"""Start the FastAPI Coordinator with `python -m kvstore`."""

import os

import uvicorn


def main() -> None:
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run("kvstore.api:app", host=host, port=port)


if __name__ == "__main__":
    main()
