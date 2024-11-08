from __future__ import annotations
from dataclasses import dataclass, field

from requests import PreparedRequest
from requests.auth import HTTPDigestAuth

from atlas_sdk.auth.config import AuthConfig, Service
from atlas_sdk.auth.profile import Profile


class ApiKeyConfig(AuthConfig):
    def __init__(
        self,
        profile: Profile = None,
        service: str | Service = Service.CLOUD,
        api_key: ApiKey = None,
        user_agent: str | None = None,
    ) -> None:
        super().__init__(
            profile or Profile("default", Service(service)), service, user_agent
        )
        self.profile.api_key = api_key or self.profile.api_key

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        digest_auth = self.profile.api_key.as_requests_auth()
        return digest_auth(r)


@dataclass
class ApiKey:
    public_key: str
    private_key: str
    _auth: HTTPDigestAuth = field(init=False)

    def __post_init__(self):
        self._auth = HTTPDigestAuth(self.public_key, self.private_key)

    def as_requests_auth(self):
        return self._auth

    @property
    def is_expired(self):
        return False
