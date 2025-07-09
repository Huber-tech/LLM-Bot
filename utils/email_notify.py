import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import time
from collections import defaultdict
# Globales Fehler-Cache mit Zeitstempel
_error_cache = defaultdict(lambda: 0)
ERROR_RATE_LIMIT_SECONDS = 3000  # 50 Minuten zwischen denselben Fehlern
load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

def send_email(subject: str, body: str):
    global _error_cache

    cache_key = f"{subject}:{body.splitlines()[0][:50]}"  # Einfache Fehler-Signatur
    now = time.time()

    if now - _error_cache[cache_key] < ERROR_RATE_LIMIT_SECONDS:
        print(f"[Email] Rate-Limit aktiv für: {cache_key}")
        return  # Abort E-Mail, Limit aktiv

    _error_cache[cache_key] = now  # Zeitstempel aktualisieren

    try:
        # Hier bleibt dein tatsächlicher Mailversand
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = os.getenv("EMAIL_FROM")
        msg['To'] = os.getenv("EMAIL_TO")

        with smtplib.SMTP_SSL(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
            server.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASS"))
            server.send_message(msg)

        print(f"[Email] Gesendet: {subject}")
    except Exception as e:
        print(f"[Email] Fehler beim Senden: {e}")
