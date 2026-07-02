"""
Application-specific exception hierarchy.

Using typed exceptions (instead of raising generic Exception/ValueError
everywhere) lets the global handler map each one to the correct HTTP status
and lets graph nodes catch specific failure modes (e.g. retry on
MetaAPIError but not on TenantNotFoundError).
"""


class AppException(Exception):
    """Base class for all application-raised exceptions."""

    def __init__(self, message: str, *, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class TenantNotFoundError(AppException):
    def __init__(self, tenant_identifier: str):
        super().__init__(
            f"Tenant not found for identifier: {tenant_identifier}",
            status_code=404,
        )


class SessionNotFoundError(AppException):
    def __init__(self, session_id: str):
        super().__init__(f"Session not found: {session_id}", status_code=404)


class InvalidWebhookSignatureError(AppException):
    def __init__(self):
        super().__init__("Webhook signature verification failed", status_code=401)


class MetaAPIError(AppException):
    """
    Raised when a call to the Meta Graph API fails after retries are
    exhausted. Carries the raw response for logging/debugging.
    """

    def __init__(self, message: str, *, response_body: str | None = None, status_code: int = 502):
        self.response_body = response_body
        super().__init__(message, status_code=status_code)


class LLMReasoningError(AppException):
    def __init__(self, message: str):
        super().__init__(f"LLM reasoning failed: {message}", status_code=502)


class MediaAssetNotFoundError(AppException):
    def __init__(self, asset_key: str, tenant_id: str):
        super().__init__(
            f"Media asset '{asset_key}' not found in media library for tenant {tenant_id}",
            status_code=404,
        )
