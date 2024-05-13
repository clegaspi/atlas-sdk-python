from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

from atlas_sdk import __version__

from atlas_sdk.auth.profile import Profile, Service


class AuthConfig(ABC):
    BASE_URL_MAPPING = {
        Service.CLOUD: "https://cloud.mongodb.com/",
        Service.GOVCLOUD: "https://cloud.mongodbgov.com/",
    }
    DEFAULT_USER_AGENT = f"atlas-sdk-python/{__version__}"

    def __init__(self, profile: Profile, user_agent: str | None = None) -> None:
        super().__init__()
        self.profile = profile
        self.service = self.profile.service
        self.user_agent = user_agent or self.DEFAULT_USER_AGENT

    @property
    def base_url(self) -> str | None:
        return self.BASE_URL_MAPPING.get(self.service)

    @abstractmethod
    def auth(self) -> Any:
        pass

    @abstractmethod
    def get_requests_config(self) -> dict:
        pass
