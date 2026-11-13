# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "tri-api",
# ]
# [[tool.uv.index]]
# name = "artifactory"
# url = "https://artifactory.trioptima.net/artifactory/api/pypi/opt-python-virtual/simple"
# default = true
# ///

# Simple example client to test imopt on OptAPI DEV.
#
# Requirements:
# uv run imopt_optapi_example.py
import json
from tri_api import AuthenticatedSession


def main():
    OPT_API_CLIENT_ID = "f817cb52-c003-11e9-acd3-54bf649d1d8a"
    OPT_USER_SCOPE = OPT_API_CLIENT_ID + ":optapi_user"
    AUTH_CLIENT_ID = "a2caed62-e28d-11e4-86da-b39459ee2d75"
    AUTH_CLIENT_SECRET = "password"

    # Use auth application to log in since the client id and client secret is fixed for a scratch installation
    session = AuthenticatedSession(
        client_id=AUTH_CLIENT_ID,
        client_secret=AUTH_CLIENT_SECRET,
        username="optapi_example",  # Default test user in DEV
        password="Passw0rd!",
        scope=f"global {OPT_USER_SCOPE}",
        base_url="https://dev.trioptima.net/",
    )

    response_docs = session.get("/opt/api/imopt/openapi.json")
    docs = response_docs.json()
    parameters = docs["paths"]["/imopt/versions/{version}"]["post"]["parameters"]
    parameters = json.dumps(parameters, indent=4)
    print("\n".join(parameters.splitlines()[:100]))


if __name__ == "__main__":
    main()
