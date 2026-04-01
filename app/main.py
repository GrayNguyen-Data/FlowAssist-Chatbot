from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.routing import Mount

from app.api.router import api_router
from app.core.config import settings
from app.mcp_server import mcp


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "FlowAssist backend is running"}


app.include_router(api_router, prefix=settings.API_PREFIX)
app.mount("/mcp", mcp.streamable_http_app())