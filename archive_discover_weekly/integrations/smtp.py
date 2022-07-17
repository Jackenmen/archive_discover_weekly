from email.message import EmailMessage
from smtplib import SMTP, SMTP_SSL
from typing import Any, Dict
import datetime
import traceback

# TODO: Move formatter to separate integration
from .base_integration import BaseIntegration


class SMTPIntegration(BaseIntegration):
    DEFAULT_SETTINGS = {
        "host": "localhost",
        "port": 25,
        "use_ssl": False,
        "authentication_required": False,
        "user": "",
        "password": "",
        "mail_from": "",
        "mail_to": "",
        "mail_subject_on_success": "",
        "mail_subject_on_error": "",
    }

    def send_tracks(self, tracks: Dict[str, Any]):
        plain_content = ""
        html_content = "<html><body><ul>"
        track: Any
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
                for a in track["artists"]
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
        self._send_mail(
            datetime.date.today().strftime(self.settings["mail_subject_on_success"]),
            plain_content,
            html_content,
        )

    def send_error(self, exception: BaseException):
        tb_str = "".join(
            traceback.format_exception(None, exception, exception.__traceback__)
        )
        self._send_mail(
            datetime.date.today().strftime(self.settings["mail_subject_on_error"]),
            f"Archiving Discover Weekly for this Week was unsuccessful.\n\n{tb_str}",
        )

    def _send_mail(self, subject: str, plain_content: str, html_content: str = ""):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.settings["mail_from"]
        msg["To"] = self.settings["mail_to"]
        msg.set_content(plain_content)
        if html_content:
            msg.add_alternative(html_content, subtype="html")
        smtp_class = SMTP_SSL if self.settings["use_ssl"] else SMTP
        with smtp_class(self.settings["host"], self.settings["port"]) as smtp:
            smtp.ehlo_or_helo_if_needed()
            if not self.settings["use_ssl"]:
                smtp.starttls()
                if not self.settings["authentication_required"]:
                    smtp.ehlo_or_helo_if_needed()
            if self.settings["authentication_required"]:
                smtp.login(self.settings["user"], self.settings["password"])
            smtp.send_message(msg)
