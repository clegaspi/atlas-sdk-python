import requests

from atlas_sdk.auth.oauth import OAuthConfig


class ApiClient:
    def __init__(self, profile) -> None:
        self.profile = profile
