"""
X-Hub-Signature-256 verification (bonus/security requirement).

Meta signs every webhook payload with HMAC-SHA256 using the app secret.
Verifying this proves the request genuinely originated from Meta and
wasn't spoofed — critical since the webhook is a public, unauthenticated
endpoint by necessity.
"""
import hashlib
import hmac

from app.config.settings import get_settings


def verify_meta_signature(raw_body: bytes, signature_header: str | None) -> bool:
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    settings = get_settings()
    expected_signature = hmac.new(
        key=settings.meta_app_secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    provided_signature = signature_header.removeprefix("sha256=")
    # Constant-time comparison — avoids timing-attack leakage of the expected signature.
    return hmac.compare_digest(expected_signature, provided_signature)
