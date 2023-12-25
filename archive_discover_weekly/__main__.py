from email.message import EmailMessage
from pathlib import Path
from smtplib import SMTP
from typing import Any, Dict, NamedTuple
import datetime
import json
import time
import traceback

import requests

from .errors import PlaylistNotModified

fields = "snapshot_id,tracks.items(track(uri,album(name,external_urls.spotify),artists,name,external_urls.spotify))"
settings_file = Path(__file__).absolute().parent / "settings.json"


class TokenInfo(NamedTuple):
    access_token: str
    expires_at: int

    @classmethod
    def from_token_data(cls, settings):
        return cls(settings["access_token"], settings["expires_at"])


def get_settings():
    with settings_file.open() as fp:
        return dict(
            {
                "last_snapshot_id": "",
                "client_id": "",
                "client_secret": "",
                "playlist_id": "",
                "access_token": "",
                "expires_at": 0,
                "refresh_token": "",
            },
            **json.load(fp),
        )


def save_settings(data: Dict[str, Any]):
    with settings_file.open("w") as fp:
        json.dump(data, fp)


def get_access_token(
    session: requests.Session, settings: Dict[str, Any], force_refresh: bool = False
):
    token_info = TokenInfo.from_token_data(settings["token_data"])
    if token_info.expires_at - time.time() > 60 and not force_refresh:
        return token_info
    token_data = session.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": settings["refresh_token"],
        },
        auth=requests.auth.HTTPBasicAuth(
            settings["client_id"].encode("utf-8"),
            settings["client_secret"].encode("utf-8"),
        ),
    ).json()
    settings["token_data"] = token_data
    return TokenInfo.from_token_data(token_data)


def get_playlist_data(settings: Dict[str, Any]):
    with requests.Session() as session:
        token_info = get_access_token(session, settings)
        return session.get(
            f"https://api.spotify.com/v1/playlists/{settings['playlist_id']}",
            params={"fields": fields},
            headers={"Authorization": f"Bearer {token_info.access_token}"},
        ).json()


def main():
    settings = get_settings()
    last_snapshot_id = settings["last_snapshot_id"]
    data = get_playlist_data(settings)
    snapshot_id = data["snapshot_id"]
    if last_snapshot_id == snapshot_id:
        raise PlaylistNotModified("Playlist wasn't modified since last check.")
    settings["last_snapshot_id"] = snapshot_id
    return sorted(data["tracks"]["items"], key=lambda t: t["track"]["name"])


if __name__ == "__main__":
    settings = get_settings()
    from integrations.smtp import SMTPIntegration

    integration = SMTPIntegration(settings["integration_settings"])
    try:
        snapshot_id, plain_content, html_content = main()
    except BaseException as e:
        sendmail(
            f"FAIL {subject}",
            f"Archiving Discover Weekly for this Week was unsuccessful.\n\n{tb_str}",
        )
        raise
    else:
        sendmail(subject, plain_content, html_content)
        save_snapshot_id(snapshot_id)
