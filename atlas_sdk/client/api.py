from enum import Enum

import requests

from atlas_sdk.auth.config import AuthConfig
from atlas_sdk.auth.profile import Profile
from atlas_sdk.auth.oauth import OAuthConfig
from atlas_sdk.auth.apikey import ApiKeyConfig


class AuthType(Enum):
    API_KEY = "api_key"
    OAUTH = "oauth"


class ApiClient:
    def __init__(
        self,
        profile: Profile,
        auth_type: AuthType | str = None,
    ) -> None:
        if auth_type:
            auth_type = AuthType(auth_type)
        self.profile = profile
        self._auth_config: AuthConfig
        if self.profile.api_key or auth_type == AuthType.API_KEY:
            self._auth_type = AuthType.API_KEY
            self._auth_config = ApiKeyConfig(self.profile)
        elif self.profile.token or auth_type == AuthType.OAUTH:
            self._auth_type = AuthType.OAUTH
            self._auth_config = OAuthConfig(self.profile)
        else:
            raise ValueError(
                "Profile did not contain a valid auth method and one was not specified."
            )

    def _refresh_auth(self):
        self._auth_config.auth()
        return self._auth_config.get_session()

    @property
    def base_url(self):
        return self._auth_config.base_url

    def test_auth(self, raise_error: bool = False):
        result = self.get(self.base_url + "api/atlas/v1.0")
        if not result.ok:
            if raise_error:
                result.raise_for_status()
            return False
        return True

    def request(self, method: str, url: str, **kwargs):
        request_args = self._refresh_auth()
        # Merge headers, overriding default with those passed in
        headers = request_args.get("headers", {})
        request_args.update(kwargs)
        headers.update(kwargs.get("headers", {}))
        request_args["headers"] = headers
        return self._auth_config.get_session().request(method, url, **request_args)

    def get(self, url: str, **kwargs):
        return self.request("get", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.request("post", url, **kwargs)

    def put(self, url: str, **kwargs):
        return self.request("put", url, **kwargs)

    def patch(self, url: str, **kwargs):
        return self.request("patch", url, **kwargs)

    def delete(self, url: str, **kwargs):
        return self.request("delete", url, **kwargs)


class PublicV2ApiClient(ApiClient):
    ATLAS_ADMIN_API_VERSION = "application/vnd.atlas.2023-11-15+json"

    def __init__(
        self,
        profile: Profile,
        auth_type: AuthType | str = None,
        api_version: str | None = None,
    ) -> None:
        super().__init__(profile, auth_type)
        self.api_version = api_version or self.ATLAS_ADMIN_API_VERSION

    def request(self, method: str, url: str, **kwargs):
        kwargs["headers"] = kwargs.get("headers", {})
        kwargs["headers"]["Content-Type"] = kwargs["headers"].get(
            "Content-Type", self.api_version
        )
        kwargs["headers"]["Accept"] = kwargs["headers"].get("Accept", self.api_version)
        return super().request(method, url, **kwargs)
