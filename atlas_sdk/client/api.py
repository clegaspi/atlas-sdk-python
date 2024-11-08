import requests

from atlas_sdk.auth.config import AuthConfig
from atlas_sdk.auth.profile import Profile
from atlas_sdk.auth.oauth import OAuthConfig
from atlas_sdk.auth.apikey import ApiKeyConfig


# Auth types
API_KEY_AUTH = "apikey"
OAUTH_AUTH = "oauth"

auth_configs = {
    API_KEY_AUTH: ApiKeyConfig,
    OAUTH_AUTH: OAuthConfig,
}


class ApiClient:
    def __init__(
        self,
        auth_type: str,
        profile: Profile = None,
        user_agent: str = None,
        **auth_config,
    ) -> None:
        self.profile = profile or Profile(name="default")
        if auth_type not in auth_configs:
            raise ValueError(f"Invalid auth method: {auth_type}")
        self._auth_type = auth_type
        self._session = requests.Session()
        self._auth_config: AuthConfig = auth_configs[auth_type](
            profile=profile, user_agent=user_agent, **auth_config
        )
        self._session.auth = self._auth_config

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
        return self._session.request(method, url, **kwargs)

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
    ATLAS_ADMIN_API_VERSION = "application/vnd.atlas.2024-10-23+json"

    def __init__(
        self,
        profile: Profile = None,
        auth_type: str = None,
        api_version: str = None,
        user_agent: str = None,
        **auth_config,
    ) -> None:
        super().__init__(auth_type, profile, user_agent, **auth_config)
        self.api_version = api_version or self.ATLAS_ADMIN_API_VERSION
        self.api_base_url = super().base_url + "api/atlas/v2/"

    def request(self, method: str, url: str, **kwargs):
        kwargs["headers"] = kwargs.get("headers", {})
        kwargs["headers"]["Content-Type"] = kwargs["headers"].get(
            "Content-Type", self.api_version
        )
        kwargs["headers"]["Accept"] = kwargs["headers"].get("Accept", self.api_version)
        return super().request(method, url, **kwargs)

    def test_auth(self, raise_error: bool = False):
        result = self.get(self.api_base_url)
        if not result.ok:
            if raise_error:
                result.raise_for_status()
            return False
        return True
