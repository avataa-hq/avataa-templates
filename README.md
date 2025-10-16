# Object Templates

## Environment variables

```toml
DB_HOST=<pgbouncer/postgres_host>
DB_NAME=<pgbouncer/postgres_object_templates_db_name>
DB_PASS=<pgbouncer/postgres_object_templates_password>
DB_PORT=<pgbouncer/postgres_port>
DB_SCHEMA=public
DB_TYPE=postgresql+asyncpg
DB_USER=<pgbouncer/postgres_object_templates_user>
DOCS_CUSTOM_ENABLED=<True/False>
DOCS_REDOC_JS_URL=<redoc_js_url>
DOCS_SWAGGER_CSS_URL=<swagger_css_url>
DOCS_SWAGGER_JS_URL=<swagger_js_url>
INVENTORY_GRPC_PORT=<inventory_grpc_port>
INVENTORY_HOST=<inventory_host>
KAFKA_CONSUMER_OFFSET=earliest
KAFKA_GROUP_ID=Object_Templates
KAFKA_INVENTORY_CHANGES_TOPIC=inventory.changes
KAFKA_SASL_MECHANISM=<kafka_sasl_mechanism>
KAFKA_SECURITY_PROTOCOL=<kafka_security_protocol>
KAFKA_TURN_ON=<True/False>
KAFKA_URL=<kafka_host>:<kafka_port>
KAFKA_WITH_KEYCLOAK=<True/False>
KEYCLOAK_CLIENT_ID=<kafka_client>
KEYCLOAK_CLIENT_SECRET=<kafka_client_secret>
KEYCLOAK_HOST=<keycloak_host>
KEYCLOAK_PORT=<keycloak_port>
KEYCLOAK_PROTOCOL=<keycloak_protocol>
KEYCLOAK_REALM=avataa
KEYCLOAK_REDIRECT_HOST=<keycloak_external_host>
KEYCLOAK_REDIRECT_PORT=<keycloak_external_port>
KEYCLOAK_REDIRECT_PROTOCOL=<keycloak_external_protocol>
KEYCLOAK_SCOPE=<keycloak_scope>
SECURITY_MIDDLEWARE_HOST=<security_middleware_host>
SECURITY_MIDDLEWARE_PORT=<security_middleware_port>
SECURITY_MIDDLEWARE_PROTOCOL=<security_middleware_protocol>
SECURITY_TYPE=<security_type>
```

### Compose

- `REGISTRY_URL` - Docker registry URL, e.g. `harbor.domain.com`
- `PLATFORM_PROJECT_NAME` - Docker registry project Docker image can be downloaded from, e.g. `avataa`


# Setup Instructions

1. Clone the repository
2. Create a .env file and set variables respectively to .env.example
3. Run the migrations using `alembic upgrade head` and check out your tables
4. Run the application inside app/ using `uvicorn main:app --reload`