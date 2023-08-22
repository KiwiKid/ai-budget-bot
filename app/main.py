from fastapi import FastAPI

from app.config import Settings
from app.routes import router
from fastapi.staticfiles import StaticFiles
from app.utils import load_dotenv_safe

settings = Settings()


def get_app() -> FastAPI:
    """Create a FastAPI app with the specified settings."""

    app = FastAPI(**settings.fastapi_kwargs)

    app.include_router(router)

    return app


load_dotenv_safe()


app = get_app()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
