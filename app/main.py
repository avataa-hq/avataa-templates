from fastapi.middleware.cors import CORSMiddleware

from config import setup_config
from init_app import create_app
from di import init_dependencies
from presentation.api.v1.endpoints import (
    template_registry_router,
    template_object_router,
    template_router,
    template_parameter_router,
)

app_title = "Object Templates"
prefix = f"/api/{app_title.replace(' ', '_').lower()}"
app_version = "1"

app = create_app(
    documentation_enabled=setup_config().app.docs_enabled,
    root_path=prefix,
    title=app_title,
    version=app_version,
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
init_dependencies(v1_app)
