from typing import Any

from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from starlette.requests import Request
from starlette.responses import HTMLResponse

from config import setup_config


def register_static_docs_routes(
    app: FastAPI,
) -> None:
    root_path = app.root_path.rstrip("/")
    if app.openapi_url is None:
        openapi_url = ""
    else:
        openapi_url = root_path + app.openapi_url
    oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url
    conf = setup_config().app
    if oauth2_redirect_url:
        oauth2_redirect_url = root_path + oauth2_redirect_url

    async def custom_swagger_ui_html(
        req: Request,
    ) -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url=openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=oauth2_redirect_url,
            swagger_js_url=conf.swagger_js_url,
            swagger_css_url=conf.swagger_css_url,
        )

    docs_url = app.docs_url or "/docs"
    if conf.swagger_js_url and conf.swagger_css_url:
        app.add_route(
            docs_url,
            custom_swagger_ui_html,
            include_in_schema=False,
        )
    # else:
    #     warnings.warn(
    #         f'Endpoint "{docs_url}" disabled. Environment variables "REDOC_JS_URL" or "SWAGGER_CSS_URL" are not set')

    async def swagger_ui_redirect(
        req: Request,
    ) -> HTMLResponse:
        return get_swagger_ui_oauth2_redirect_html()

    swagger_ui_oauth2_redirect_url = (
        app.swagger_ui_oauth2_redirect_url or "/docs/oauth2-redirect"
    )
    app.add_route(
        swagger_ui_oauth2_redirect_url,
        swagger_ui_redirect,
        include_in_schema=False,
    )

    async def redoc_html(
        req: Request,
    ) -> HTMLResponse:
        return get_redoc_html(
            openapi_url=openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url=conf.redoc_js_url,
        )

    redoc_url = app.redoc_url or "/redoc"
    if conf.redoc_js_url:
        app.add_route(
            redoc_url,
            redoc_html,
            include_in_schema=False,
        )
    # else:
    #     warnings.warn(f'Endpoint "{redoc_url}" disabled. Environment variable "REDOC_JS_URL" is not set')


def create_app(documentation_enabled: bool, **kwargs: Any) -> FastAPI:
    conf = setup_config().app
    options = kwargs
    if not documentation_enabled:
        options["openapi_url"] = None
    elif conf.custom_enabled:
        if conf.swagger_js_url and conf.swagger_css_url:
            options["docs_url"] = None
        if conf.redoc_js_url:
            options["redoc_url"] = None
    app = FastAPI(**options)
    if documentation_enabled and conf.custom_enabled:
        register_static_docs_routes(app)
    return app
