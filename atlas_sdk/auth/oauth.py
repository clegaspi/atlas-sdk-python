from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from time import sleep
from urllib.parse import urlencode
from typing import TYPE_CHECKING
import webbrowser

import jwt
import requests

from atlas_sdk import __version__
from atlas_sdk.auth.profile import Profile, Service
from atlas_sdk.auth.config import AuthConfig

AUTH_EXPIRED_ERROR = "DEVICE_AUTHORIZATION_EXPIRED"


class TimeoutError(BaseException):
    pass


@dataclass
class DeviceCode:
    user_code: str
    verification_uri: str
    device_code: str
    expires_in: int
    interval: int
    issue_time: datetime = field(default_factory=datetime.now)

    @property
    def now(self):
        return datetime.now()

    @property
    def is_expired(self):
        return self.now > self.issue_time + timedelta(seconds=self.expires_in)

    def sleep(self):
        sleep(self.interval)


@dataclass
class Token:
    access_token: str
    refresh_token: str
    scope: str
    id_token: str
    token_type: str
    expires_in: int
    issue_time: datetime = field(default_factory=datetime.now)
    access_revoked: bool = False
    refresh_revoked: bool = False

    @property
    def revoked(self):
        return self.access_revoked or self.refresh_revoked

    @property
    def expiry(self):
        self.issue_time + timedelta(seconds=self.expires_in)

    @property
    def is_expired(self):
        return self.revoked or datetime.now() > self.expiry

    @property
    def claims(self):
        # No authentication is being done. Only reading the claims.
        return jwt.decode(
            self.access_token,
            options={"verify_signature": False},
        )


@dataclass
class RegistrationConfig:
    registration_url: str


class OAuthConfig(AuthConfig):
    DEVICE_BASE_PATH = "api/private/unauth/account/device"
    # Taken from Atlas CLI
    CLOUD_CLIENT_ID = "0oabtxactgS3gHIR0297"
    GOVCLOUD_CLIENT_ID = "0oabtyfelbTBdoucy297"

    def __init__(self, profile: Profile, user_agent: str = None) -> None:
        super().__init__(profile, user_agent)
        if self.profile.service == Service.CLOUD:
            self.client_id = self.CLOUD_CLIENT_ID
        elif self.profile.service == Service.GOVCLOUD:
            self.client_id = self.GOVCLOUD_CLIENT_ID
        else:
            raise ValueError(f"Unexpected value for service: {self.profile.service}")

        self._default_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }

        self._default_scopes = " ".join(
            [
                "openid",
                "profile",
                "offline_access",
            ]
        )

    def _do_request(
        self, endpoint: str, body: dict, method: str = "post"
    ) -> requests.Response:
        url = self.base_url + self.DEVICE_BASE_PATH + f"/{endpoint}"
        return getattr(requests, method)(
            url,
            data=urlencode(body) if body else None,
            headers=self._default_headers,
        )

    def auth(self, open_browser: bool = True) -> Token:
        if self.profile.token:
            if not self.profile.token.is_expired:
                return self.profile.token
            return self.refresh_token(self.profile.token, reauth_if_expired=True)
        code = self.request_code()

        print(f"Navigate to {code.verification_uri} for authentication")
        print(f"Enter the code {code.user_code} to authorize this client")

        if open_browser:
            webbrowser.open(code.verification_uri)

        self.profile.token = self.poll_token(code)
        username = self.profile.token.claims["sub"]
        print(f"Successfully authenticated as {username}")
        return self.profile.token

    def get_requests_config(self) -> dict:
        return {
            "headers": {"Authorization": f"Bearer {self.profile.token.access_token}"}
        }

    def request_code(self) -> DeviceCode:
        result = self._do_request(
            "authorize",
            {
                "client_id": self.client_id,
                "scope": self._default_scopes,
            },
        )

        if not result.ok:
            result.raise_for_status()
        return DeviceCode(**result.json())

    def get_token(self, device_code: DeviceCode) -> Token | None:
        result = self._do_request(
            "token",
            {
                "client_id": self.client_id,
                "device_code": device_code.device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
        )

        if not result.ok:
            if (
                result.status_code == 400
                and result.json().get("errorCode") == "DEVICE_AUTHORIZATION_PENDING"
            ):
                return None
            result.raise_for_status()

        return Token(**result.json())

    def poll_token(self, device_code: DeviceCode) -> Token:
        if device_code.now < device_code.issue_time + timedelta(device_code.interval):
            device_code.sleep()
        while not device_code.is_expired:
            token = self.get_token(device_code)
            if token:
                return token
            device_code.sleep()
        raise TimeoutError("Timed out waiting for user to authenticate.")

    def refresh_token(self, token: Token, reauth_if_expired: bool = True) -> Token:
        result = self._do_request(
            "token",
            {
                "client_id": self.client_id,
                "refresh_token": token.refresh_token,
                "scope": self._default_scopes,
                "grant_type": "refresh_token",
            },
        )

        if not result.ok:
            if reauth_if_expired:
                print("Refresh token expired. Reauthentication required.")
                return self.auth(open_browser=True)
            result.raise_for_status()

        self.profile.token = Token(**result.json())
        return self.profile.token

    def revoke_token(self, token: Token, token_type: str) -> bool:
        if token_type == "refresh":
            token_value = token.refresh_token
        elif token_type == "access":
            token_value = token.access_token
        else:
            raise ValueError("token_type must be 'refresh' or 'access'")

        result = self._do_request(
            "revoke",
            {
                "client_id": self.client_id,
                "token": token_value,
                "token_type_hint": token_type,
            },
        )

        if not result.ok:
            result.raise_for_status()
        token.revoked = True
        return True

    def get_registration_config(self):
        pass
        """
        // RegistrationConfig retrieves the config used for registration.
        func (c Config) RegistrationConfig(ctx context.Context) (*RegistrationConfig, *core.Response, error) {
            req, err := c.NewRequest(ctx, http.MethodGet, deviceBasePath+"/registration", url.Values{})
            if err != nil {
                return nil, nil, err
            }
            var rc *RegistrationConfig
            resp, err := c.Do(ctx, req, &rc)
            if err != nil {
                return nil, resp, err
            }
            return rc, resp, err
        }
        """
