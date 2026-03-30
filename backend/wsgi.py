from importlib import import_module

from app import app

if __name__ == "__main__":
    uvicorn = import_module("uvicorn")
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=False)
