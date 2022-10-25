from django.conf import settings


INCLUSION_CONNECT_SCOPES = "openid profile email"

INCLUSION_CONNECT_CLIENT_ID = settings.INCLUSION_CONNECT_CLIENT_ID
INCLUSION_CONNECT_CLIENT_SECRET = settings.INCLUSION_CONNECT_CLIENT_SECRET

INCLUSION_CONNECT_REALM_ENDPOINT = "{base_url}/realms/{realm}/protocol/openid-connect".format(
    base_url=settings.INCLUSION_CONNECT_BASE_URL, realm=settings.INCLUSION_CONNECT_REALM
)
INCLUSION_CONNECT_ENDPOINT_AUTHORIZE = f"{INCLUSION_CONNECT_REALM_ENDPOINT}/auth"
INCLUSION_CONNECT_ENDPOINT_REGISTER = f"{INCLUSION_CONNECT_REALM_ENDPOINT}/registrations"
INCLUSION_CONNECT_ENDPOINT_TOKEN = f"{INCLUSION_CONNECT_REALM_ENDPOINT}/token"
INCLUSION_CONNECT_ENDPOINT_USERINFO = f"{INCLUSION_CONNECT_REALM_ENDPOINT}/userinfo"
INCLUSION_CONNECT_ENDPOINT_LOGOUT = f"{INCLUSION_CONNECT_REALM_ENDPOINT}/logout"

# These expiration times have been chosen arbitrarily.
INCLUSION_CONNECT_TIMEOUT = 60

INCLUSION_CONNECT_SESSION_KEY = "inclusion_connect"
