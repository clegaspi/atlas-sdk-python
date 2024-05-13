from dataclasses import dataclass, field

from requests.auth import HTTPDigestAuth


@dataclass
class ApiKeyConfig:
    public_key: str
    private_key: str
    _auth: HTTPDigestAuth = field(init=False)

    def __post_init__(self):
        self._auth = HTTPDigestAuth(self.public_key, self.private_key)

    def auth(self):
        return self._auth

    @property
    def is_expired(self):
        return False
