"""
Centralized application configuration.

All environment variables are declared here and nowhere else. This is the
single source of truth for config — no os.getenv() calls should appear
anywhere else in the codebase. Pydantic Settings gives us validation
(fails fast on startup if a required var is missing) and type coercion.
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    app_name: str = "WhatsApp AI SaaS"
    environment: str = Field(default="development")  # development | production
    log_level: str = Field(default="INFO")
    port: int = Field(default=8000)

    # --- CORS ---
    # Comma-separated origins in the env var, e.g. "https://app.example.com,http://localhost:5173"
    cors_allowed_origins: str = Field(
        default="http://localhost:5173,http://localhost:4173,https://krid-kaws-1.onrender.com"
    )

    # --- MongoDB ---
    mongodb_uri: str = Field(..., description="MongoDB Atlas connection string")
    mongodb_db_name: str = Field(default="whatsapp_saas")

    # --- Gemini ---
    gemini_api_key: str = Field(..., description="Gemini API key")
    gemini_model: str = Field(default="gemini-2.5-flash")
    gemini_vision_model: str = Field(default="gemini-2.5-flash")

    # --- Meta WhatsApp Cloud API ---
    meta_app_secret: str = Field(..., description="Used to validate X-Hub-Signature-256")
    meta_webhook_verify_token: str = Field(..., description="Used for GET webhook verification challenge")
    meta_access_token: str = Field(..., description="Permanent/long-lived Graph API access token")
    meta_phone_number_id: str = Field(..., description="Default WhatsApp Business phone number ID")
    meta_graph_api_version: str = Field(default="v20.0")

    # --- Typing indicator heartbeat ---
    typing_heartbeat_interval_seconds: int = Field(default=20)

    # --- Sentiment / handover threshold ---
    # sentiment_score is expected in range [0.0, 1.0], where higher = more frustrated.
    handover_sentiment_threshold: float = Field(default=0.75)

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    @property
    def graph_api_base_url(self) -> str:
        return f"https://graph.facebook.com/{self.meta_graph_api_version}"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor. Use this everywhere instead of instantiating
    Settings() directly, so we only parse/validate env vars once per process.
    """
    return Settings()
