from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
import os

env = os.getenv("ENV", "local")
load_dotenv("default.env")
load_dotenv(".env", override=True)
load_dotenv(f".env.{env}", override=True)


class AppConfig(BaseSettings):
    """Application configuration loaded from environment variables."""

    # App
    env: str = Field(default="local", alias="ENV")
    project_name: str = Field(default="marketing-service", alias="PROJECT_NAME")
    base_path: str = Field(default="/marketing-service/api/v1", alias="BASE_PATH")
    debug: bool = Field(default=False, alias="DEBUG")

    # Database
    db_url: str = Field(default="postgresql+psycopg://postgres:postgres@localhost:5432/marketing", alias="DB_URL")
    db_schema: str = Field(default="marketing", alias="DB_SCHEMA")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")

    # WhatsApp Cloud API
    whatsapp_phone_number_id: str = Field(default="", alias="WHATSAPP_PHONE_NUMBER_ID")
    whatsapp_access_token: str = Field(default="", alias="WHATSAPP_ACCESS_TOKEN")
    whatsapp_verify_token: str = Field(default="", alias="WHATSAPP_VERIFY_TOKEN")
    whatsapp_business_account_id: str = Field(default="", alias="WHATSAPP_BUSINESS_ACCOUNT_ID")

    # Anthropic (Claude)
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    claude_default_model: str = Field(default="claude-sonnet-4-20250514", alias="CLAUDE_DEFAULT_MODEL")

    # Google (Gemini)
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_default_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_DEFAULT_MODEL")

    # OpenRouter (free models fallback)
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_default_model: str = Field(default="deepseek/deepseek-chat-v3-0324:free", alias="OPENROUTER_DEFAULT_MODEL")

    # Instagram / Meta Graph API
    instagram_access_token: str = Field(default="", alias="INSTAGRAM_ACCESS_TOKEN")
    instagram_business_account_id: str = Field(default="", alias="INSTAGRAM_BUSINESS_ACCOUNT_ID")

    # AWS S3 / Cloudflare R2
    aws_access_key_id: str = Field(default="", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="", alias="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="ap-south-1", alias="AWS_REGION")
    s3_bucket_name: str = Field(default="marketing-assets", alias="S3_BUCKET_NAME")
    s3_endpoint_url: str = Field(default="", alias="S3_ENDPOINT_URL")

    # Razorpay (Phase 2)
    razorpay_key_id: str = Field(default="", alias="RAZORPAY_KEY_ID")
    razorpay_key_secret: str = Field(default="", alias="RAZORPAY_KEY_SECRET")

    # Observability
    otlp_grpc_endpoint: str = Field(default="", alias="OTLP_GRPC_ENDPOINT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    class Config:
        populate_by_name = True
        env_file = ".env"
        extra = "ignore"


app_config = AppConfig()
