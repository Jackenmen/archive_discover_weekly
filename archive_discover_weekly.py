#!/usr/bin/python3
import datetime
import os
import traceback
from email.message import EmailMessage
from smtplib import SMTP

import requests

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"].encode()
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"].encode()
REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_TO = os.environ["EMAIL_TO"]
PLAYLIST_ID = os.environ["SPOTIFY_PLAYLIST_ID"]

fields = "snapshot_id,tracks.items(track(uri,album(name,external_urls.spotify),artists,name,external_urls.spotify))"


class PlaylistNotModified(Exception):
    """Raised when snapshot id is the same as before."""


def get_snapshot_id():
    with open("archive_discover_weekly.txt", "a+") as f:
        f.seek(0)
        return f.read()


def save_snapshot_id(snapshot_id: str):
    with open("archive_discover_weekly.txt", "w+") as f:
        f.write(snapshot_id)


def get_access_token(session: requests.Session):
    return session.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
        auth=requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
    ).json()["access_token"]


def get_playlist_data():
    with requests.Session() as session:
        access_token = get_access_token(session)
        return session.get(
            f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}",
            params={"fields": fields},
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()


def sendmail(subject: str, plain_content: str, html_content: str = ""):
    with SMTP("localhost") as smtp:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"Discover Weekly Archive <{EMAIL_FROM}>"
        msg["To"] = EMAIL_TO
        msg.set_content(plain_content)
        if html_content:
            msg.add_alternative(html_content, subtype="html")
        smtp.send_message(msg)


def main():
    old_snapshot_id = get_snapshot_id()
    data = get_playlist_data()
    snapshot_id = data["snapshot_id"]
    if old_snapshot_id == snapshot_id:
        raise PlaylistNotModified("Playlist wasn't modified since last check.")
    plain_content = ""
    html_content = "<html><body><ul>"
    tracks = sorted(data["tracks"]["items"], key=lambda t: t["track"]["name"])
    for idx, track in enumerate(tracks, 1):
        track = track["track"]
        plain_content += (
            f"{idx}. {track['name']}\n"
            f"Artist names: {', '.join(a['name'] for a in track['artists'])}\n"
            f"Album name: {track['album']['name']}\n"
            f"Spotify URL: {track['external_urls']['spotify']}\n"
            f"Spotify URI: {track['uri']}\n"
        )
        artists = ", ".join(
            f"<a href=\"{a['external_urls']['spotify']}\">{a['name']}</a>"
            for a in track['artists']
        )
        html_content += (
            f"<li><a href=\"{track['external_urls']['spotify']}\"><b>"
            f"{track['name']}"
            "</b></a><br>"
            f"Artist names: {artists}<br>"
            f"Album name: <a href=\"{track['album']['external_urls']['spotify']}\">"
            f"{track['album']['name']}"
            "</a><br>"
            f"Spotify URI: {track['uri']}</li>"
        )
    html_content += "</ul></body></html>"
    return snapshot_id, plain_content, html_content


if __name__ == "__main__":
    subject = datetime.date.today().strftime(
        "Discover Weekly Archive - Week %V, %Y (%d.%m)"
    )
    try:
        snapshot_id, plain_content, html_content = main()
    except BaseException as e:
        tb_str = "".join(traceback.format_exception(None, e, e.__traceback__))
        sendmail(
            f"FAIL {subject}",
            f"Archiving Discover Weekly for this Week was unsuccessful.\n\n{tb_str}",
        )
        raise
    else:
        sendmail(subject, plain_content, html_content)
        save_snapshot_id(snapshot_id)
