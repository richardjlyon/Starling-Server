import sys
from pathlib import Path

import uvicorn


def set_path():
    """Add project root to system path for submodule searching."""
    BASE_DIR = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(BASE_DIR))


if __name__ == "__main__":
    set_path()
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)
