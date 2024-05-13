from enum import Enum

import requests

from atlas_sdk.auth.profile import Profile
from atlas_sdk.auth.oauth import OAuthConfig
from atlas_sdk.auth.apikey import ApiKeyConfig


class AuthType(Enum):
    API_KEY = "api_key"
    OAUTH = "oauth"


class ApiClient:
    def __init__(self, profile: Profile) -> None:
        self._auth_config: OAuthConfig | ApiKeyConfig
        self.profile = profile
        if self.profile.api_key:
            self._auth_type = AuthType.API_KEY
            self._auth_config = self.profile.api_key
        elif self.profile.token:
            self._auth_type = AuthType.OAUTH
            self._auth_config = OAuthConfig(self.profile)

    def _refresh_auth(self):
        self._auth_config.auth()
        if self._auth_type == AuthType.API_KEY:
            return {"auth": self.profile.api_key.auth()}
        elif self._auth_type == AuthType.OAUTH:
            return {
                "headers": {
                    "Authorization": f"Bearer {self._auth_config.auth().access_token}"
                }
            }

    def request(self, method, url, **kwargs):
        request_args = self._refresh_auth()
        request_args.update(kwargs)
        return requests.request(method, url, **request_args)

    def get(self, url, **kwargs):
        return self.request("get", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("post", url, **kwargs)

    def put(self, url, **kwargs):
        return self.request("put", url, **kwargs)

    def patch(self, url, **kwargs):
        return self.request("patch", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("delete", url, **kwargs)
