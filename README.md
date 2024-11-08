# Atlas API SDK for Python

The SDK provides a wrapper around the Python `requests` library to handle authentication by OAuth and API key pair (digest). Here are some examples of use:

```python
from atlas_sdk.client.api import ApiClient, PublicV2ApiClient, OAUTH_AUTH, API_KEY_AUTH
from atlas_sdk.auth.apikey import ApiKey
from atlas_sdk.auth.profile import Profile

# AuthType.OAUTH for OIDC login with Atlas account, AuthType.API_KEY for digest auth
# ApiClient for general client to all Atlas APIs (except app services)
# PublicV2ApiClient is for targeting Atlas Admin API v2

# open_browser=True is the default, but this illustrates that you can pass
# down kwargs specific to the auth config
client_v2 = PublicV2ApiClient(auth_type=OAUTH_AUTH, open_browser=True)

# Pushing down the API key to the auth config. You can also do this with a Profile
# but profiles are not necessary if you are not reusing authentication between
# clients or don't want to load/save credentials to disk
api_key = ApiKey(public_key="abcdefgh", private_key="xxxxxxxxxx")
client_general = ApiClient(
    auth_type=API_KEY_AUTH,
    api_key=api_key,
)
client_general = ApiClient(
    profile=Profile(name="myprofile", api_key=api_key),
    # Profiles can contain multiple credential types, so you must
    # explicitly specify which one to use
    auth_type=API_KEY_AUTH,
)
if client_v2.test_auth():
    # You don't have to test auth first to gather the token
    print("Auth successful")

response = client_v2.get(client_v2.api_base_url + "orgs")
# response is a requests Response object
```
