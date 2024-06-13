from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from requests import Session
from requests.auth import HTTPDigestAuth

from atlas_sdk.auth.config import AuthConfig

if TYPE_CHECKING:
    from atlas_sdk.auth.profile import Profile


class ApiKeyConfig(AuthConfig):
    def __init__(
        self, profile: Profile, api_key: ApiKey = None, user_agent: str | None = None
    ) -> None:
        super().__init__(profile, user_agent)
        self.api_key = api_key or self.profile.api_key
        self.profile.api_key = self.api_key
        self.session = None

    def auth(self):
        return self.api_key.as_requests_auth()

    def get_session(self) -> Session:
        if not self.session:
            self.session = Session()
            self.session.auth = self.auth()
        return self.session


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
