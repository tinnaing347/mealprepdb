import logging
import fastapi_auth0
from typing import Dict, Any

logger = logging.getLogger("fastapi_auth0")

# config for auth
from ..config import AUTH0_AUDIENCE, AUTH0_DOMAIN, AUTH0_ORG_ID


SCOPES: Dict[str, Any] = {}
auth0 = fastapi_auth0.Auth0(
    domain=AUTH0_DOMAIN, api_audience=AUTH0_AUDIENCE, org_id=None, scopes=SCOPES
)
