from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import setup_config
from infrastructure.grpc.config import cleanup_grpc_services, init_grpc_services
from init_app import create_app
from presentation.api.v1.endpoints import (
    template_object_router,
    template_parameter_router,
    template_registry_router,
    template_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_grpc_services()
    yield
    await cleanup_grpc_services()


app_title = setup_config().app.app_title
prefix = setup_config().app.prefix
app_version = setup_config().app.app_version

app = create_app(
    documentation_enabled=setup_config().app.docs_enabled,
    root_path=prefix,
    title=app_title,
    version=app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
v1_options = {
    "root_path": f"{prefix}/v{app_version}",
    "title": app_title,
    "version": app_version,
}
v1_app = create_app(
    documentation_enabled=setup_config().app.docs_enabled,
    **v1_options,
)

v1_app.include_router(template_registry_router.router)
v1_app.include_router(template_parameter_router.router)
v1_app.include_router(template_object_router.router)
v1_app.include_router(template_router.router)

app.mount(f"/v{app_version}", v1_app)
