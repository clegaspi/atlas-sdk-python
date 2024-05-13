from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

import tomlkit

if TYPE_CHECKING:
    from atlas_sdk.auth.oauth import Token
    from atlas_sdk.auth.apikey import ApiKey


class Service(Enum):
    CLOUD = "cloud"
    GOVCLOUD = "govcloud"

    def __eq__(self, value: object) -> bool:
        return super().__eq__(value)

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass
class Profile:
    name: str
    service: Service = Service.CLOUD
    org_id: str = None
    project_id: str = None
    api_key: ApiKey = None
    token: Token = None

    @property
    def access_token(self):
        if self.token:
            return self.token.access_token
        return None

    @property
    def refresh_token(self):
        if self.token:
            return self.token.refresh_token
        return None

    @classmethod
    def from_toml(cls, toml_data: dict):
        pass

    def to_toml(self):
        pass

    def __post_init__(self):
        if self.token and self.api_key:
            raise ValueError("Profile can only have one authentication method")