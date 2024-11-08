from __future__ import annotations
from dataclasses import dataclass
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


CLI_CONFIG_PATH = {
    "win": "%AppData/atlascli",
    "macos": "/Users/%s/Library/Application Support/atlascli",
    "linux": "$XDG_CONFIG_HOME/atlascli",
}


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
    def load_atlas_cli_config(cls):
        pass

    def write_atlas_cli_config(self):
        pass
