from starlette.requests import Request

from config import setup_config
from presentation.security.security_data_models import ClientRoles, UserData
from presentation.security.security_interface import SecurityInterface

default_user = UserData(
    id=None,
    audience=None,
    name="Anonymous",
    preferred_name="Anonymous",
    realm_access=ClientRoles(
        name="realm_access", roles=[setup_config().security_config.admin_role]
    ),
    resource_access=None,
    groups=None,
)


class DisabledSecurity(SecurityInterface):
    async def __call__(self, request: Request) -> UserData:
        return default_user
