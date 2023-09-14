""" Config for environment variables
"""
import os

ENVIRONMENT = os.environ.get("MEALPREPDB_ENVIRONMENT", "local")
POSTGRES_USER = os.environ.get("MEALPREPDB_POSTGRES_USER", "")
POSTGRES_PASSWORD = os.environ.get("MEALPREPDB_POSTGRES_PASSWORD", "")
POSTGRES_HOST = os.environ.get("MEALPREPDB_POSTGRES_HOST", "")
POSTGRES_PORT = os.environ.get("MEALPREPDB_POSTGRES_PORT", "")
POSTGRES_DB = os.environ.get("MEALPREPDB_POSTGRES_DB", "")
AUTH0_DOMAIN = os.environ.get("MEALPREPDB_AUTH0_DOMAIN", "")
AUTH0_AUDIENCE = os.environ.get("MEALPREPDB_AUTH0_AUDIENCE", "")
AUTH0_ORG_ID = os.environ.get("MEALPREPDB_AUTH0_ORG_ID", "")


# docker-compose will set these to strings if not set.
MAX_OVERFLOW = os.environ.get("MEALPREPDB_DB_ENGINE_MAX_OVERFLOW", 5)
if MAX_OVERFLOW == "":
    MAX_OVERFLOW = 5

POOL_SIZE = os.environ.get("MEALPREPDB_DB_ENGINE_POOL_SIZE", 5)
if POOL_SIZE == "":
    POOL_SIZE = 5


_POSTGRES_URI_BASE = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/"


# local -> backend dev
# remote-dev -> frontend dev deployment - allow from localhost or remote
# production -> staging or production - only remote from one of our apps
# testing -> special boi for tests

if ENVIRONMENT == "local":
    # local base url
    POSTGRES_URI = _POSTGRES_URI_BASE + f"{POSTGRES_DB}"
    ALLOW_ORIGINS = ["http://localhost", "https://localhost"]
    ALLOW_ORIGIN_REGEX = None
    DEBUG = True

elif ENVIRONMENT == "remote-dev":
    POSTGRES_URI = _POSTGRES_URI_BASE + f"{POSTGRES_DB}?ssl=require"
    DEBUG = False
    ALLOW_ORIGINS = ["http://localhost", "https://localhost"]
    ALLOW_ORIGIN_REGEX = r""

elif ENVIRONMENT == "production":
    # ssl plus allowed origin for CORS
    POSTGRES_URI = _POSTGRES_URI_BASE + f"{POSTGRES_DB}?ssl=require"
    ALLOW_ORIGINS = []
    ALLOW_ORIGIN_REGEX = r""
    DEBUG = False

# NOTE this is to hack our way through dealing with alembic in a test environment... :((
elif ENVIRONMENT == "testing":
    POSTGRES_TEST_DB = os.environ.get("MEALPREPDB_POSTGRES_TEST_DB", default="testdb")
    POSTGRES_URI = _POSTGRES_URI_BASE + f"{POSTGRES_TEST_DB}"
    ALLOW_ORIGINS = ["http://localhost", "https://localhost"]
    ALLOW_ORIGIN_REGEX = None
    DEBUG = True

else:
    raise ValueError("ENVIRONMENT must be either local, testing  or production")
