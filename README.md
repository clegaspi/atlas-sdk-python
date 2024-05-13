# Atlas API SDK for Python

The SDK provides a wrapper around the Python `requests` library to handle authentication by OAuth and API key pair (digest). Here are some examples of use:

```python
from atlas_sdk.client.api import ApiClient, PublicV2ApiClient, AuthType
from atlas_sdk.auth.profile import Profile, Service

# Service.CLOUD for commercial Atlas (default) and Service.GOVCLOUD for Atlas for Gov
profile = Profile("test_profile", service=Service.CLOUD)
# AuthType.OAUTH for OIDC login with Atlas account, AuthType.API_KEY for digest auth
# ApiClient for general client to all Atlas APIs
# PublicV2ApiClient is for targeting Atlas Admin API v2
client_general = ApiClient(profile, auth_type=AuthType.OAUTH)
client_v2 = PublicV2ApiClient(profile, auth_type=AuthType.OAUTH)
if client_v2.test_auth():
    print("Auth successful")

response = client_v2.get(client.base_url + "api/atlas/v2")
# response is a requests Response object
```
