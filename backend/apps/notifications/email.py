import json
import logging
import threading
import urllib.error
import urllib.request

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def _send_via_brevo_api(to_email, subject, text_body, html_body, api_key):
    """POST to Brevo's transactional API over HTTPS (port 443).

    HF Docker Spaces block outbound SMTP ports, so SMTP hangs; the HTTP API
    is the reliable path. Runs in a background thread, so it never blocks the
    request even if the provider is slow.
    """
    payload = {
        "sender": {"email": settings.DEFAULT_FROM_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": text_body,
    }
    if html_body:
        payload["htmlContent"] = html_body
    req = urllib.request.Request(
        BREVO_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "api-key": api_key,
            "content-type": "application/json",
            "accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            logger.info("Brevo API email sent to %s: %s (HTTP %s)", to_email, subject, resp.status)
    except urllib.error.HTTPError as exc:
        logger.error("Brevo API HTTP %s sending to %s — %s", exc.code, to_email, exc.read()[:300])
    except Exception as exc:
        logger.error("Brevo API error sending to %s — %s", to_email, exc)


def send_email(to_email, subject, text_body, html_body=None):
    """Send a transactional email. Never blocks the caller for long.

    Production: Brevo HTTP API in a daemon thread (SMTP is blocked on HF).
    Dev / no API key: Django's configured backend (console in development).
    """
    if not to_email:
        return False

    api_key = getattr(settings, "BREVO_API_KEY", "") or ""
    if api_key:
        threading.Thread(
            target=_send_via_brevo_api,
            args=(to_email, subject, text_body, html_body, api_key),
            daemon=True,
        ).start()
        return True

    try:
        send_mail(
            subject=subject,
            message=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_body,
            fail_silently=False,
        )
        logger.info("Email sent to %s: %s", to_email, subject)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s — %s", to_email, exc)
        return False
