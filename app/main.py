from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    template_registry_router,
    template_parameter_router,
    template_object_router,
    template_router,
)

prefix = "/api/template"
app_title = "Template API"
app_version = "1"


app = FastAPI(
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

v1_app = FastAPI(
    title=f"{app_title} v{app_version}",
    version=app_version,
)
v1_app.include_router(template_registry_router.router)
v1_app.include_router(template_parameter_router.router)
v1_app.include_router(template_object_router.router)
v1_app.include_router(template_router.router)

app.mount(f"/v{app_version}", v1_app)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the FastAPI example"
    }
