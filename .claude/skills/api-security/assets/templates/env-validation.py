"""
Environment Variable Validation and Configuration

Validates all required environment variables on startup with:
- Required field validation
- Format validation
- Security strength validation
- Type conversion
- Helpful error messages

Usage:
    from env_validation import config

    # Access validated config
    secret = config.BETTER_AUTH_SECRET
    db_url = config.DATABASE_URL
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field, validator
from enum import Enum


class Environment(str, Enum):
    """Valid environment values"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class Config(BaseSettings):
    """
    Application configuration with validation.

    All required environment variables are validated on startup.
    Missing or invalid variables raise clear error messages.
    """

    # ==============================================================================
    # Authentication
    # ==============================================================================

    BETTER_AUTH_SECRET: str = Field(
        ...,  # Required
        min_length=32,
        description="JWT signing secret - must match frontend secret exactly"
    )

    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm (must match frontend)"
    )

    JWT_EXPIRATION_HOURS: int = Field(
        default=24,
        ge=1,
        le=168,  # Max 1 week
        description="JWT token expiration in hours"
    )

    # ==============================================================================
    # Database
    # ==============================================================================

    DATABASE_URL: str = Field(
        ...,  # Required
        description="PostgreSQL connection string"
    )

    # ==============================================================================
    # Application
    # ==============================================================================

    ENVIRONMENT: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment"
    )

    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode (auto-enabled in development)"
    )

    HOST: str = Field(
        default="0.0.0.0",
        description="Server host"
    )

    PORT: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Server port"
    )

    # ==============================================================================
    # CORS
    # ==============================================================================

    FRONTEND_URL: Optional[str] = Field(
        default=None,
        description="Frontend URL for CORS (required in production)"
    )

    ALLOWED_ORIGINS: Optional[str] = Field(
        default=None,
        description="Comma-separated list of allowed CORS origins"
    )

    BACKEND_URL: Optional[str] = Field(
        default=None,
        description="Backend URL (required in production)"
    )

    # ==============================================================================
    # Security
    # ==============================================================================

    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Enable rate limiting"
    )

    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        ge=1,
        description="Max requests per minute per IP"
    )

    # ==============================================================================
    # Validators
    # ==============================================================================

    @validator("BETTER_AUTH_SECRET")
    def validate_secret_strength(cls, v):
        """Ensure secret is strong enough"""
        if len(v) < 32:
            raise ValueError(
                f"BETTER_AUTH_SECRET must be at least 32 characters. "
                f"Current length: {len(v)}. "
                f"Generate a strong secret with: openssl rand -hex 32"
            )

        # Check for common weak secrets
        weak_secrets = [
            "your-secret-key-here",
            "change-me",
            "secret",
            "password",
            "test",
            "development",
            "12345",
        ]

        if v.lower() in weak_secrets or v.lower().startswith("test"):
            raise ValueError(
                "BETTER_AUTH_SECRET appears to be a placeholder or test value. "
                "Generate a strong secret with: openssl rand -hex 32"
            )

        return v

    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError(
                "DATABASE_URL must be a PostgreSQL connection string. "
                "Format: postgresql://user:password@host:port/database"
            )

        # Warn about insecure connections in production
        if "sslmode=disable" in v:
            import warnings
            warnings.warn(
                "DATABASE_URL has sslmode=disable. "
                "SSL should be enabled in production for security."
            )

        return v

    @validator("FRONTEND_URL")
    def validate_frontend_url(cls, v, values):
        """Require FRONTEND_URL in production"""
        environment = values.get("ENVIRONMENT")

        if environment == Environment.PRODUCTION and not v:
            raise ValueError(
                "FRONTEND_URL is required in production. "
                "Example: https://app.example.com"
            )

        if v and not v.startswith(("http://", "https://")):
            raise ValueError(
                f"FRONTEND_URL must start with http:// or https://. Got: {v}"
            )

        return v

    @validator("DEBUG")
    def auto_enable_debug_in_dev(cls, v, values):
        """Auto-enable debug in development"""
        environment = values.get("ENVIRONMENT")

        if environment == Environment.DEVELOPMENT:
            return True

        return v

    # ==============================================================================
    # Computed Properties
    # ==============================================================================

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def cors_origins(self) -> list[str]:
        """Get CORS allowed origins as list"""
        if self.ALLOWED_ORIGINS:
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

        if self.is_production:
            if not self.FRONTEND_URL:
                raise ValueError("FRONTEND_URL required in production")
            return [self.FRONTEND_URL]

        # Development defaults
        return [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
        ]

    # ==============================================================================
    # Configuration
    # ==============================================================================

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# ==============================================================================
# Load and Validate Configuration
# ==============================================================================

def load_config() -> Config:
    """
    Load and validate configuration.

    Returns:
        Config: Validated configuration object

    Raises:
        ValueError: If required variables are missing or invalid
        ValidationError: If validation fails
    """
    try:
        config = Config()
        print("✓ Configuration loaded and validated")
        print(f"✓ Environment: {config.ENVIRONMENT.value}")
        print(f"✓ Debug mode: {config.DEBUG}")
        print(f"✓ CORS origins: {config.cors_origins}")
        return config

    except Exception as e:
        print("\n❌ Configuration Error:\n")
        print(str(e))
        print("\nRequired environment variables:")
        print("  BETTER_AUTH_SECRET - JWT signing secret (32+ chars)")
        print("  DATABASE_URL - PostgreSQL connection string")
        print("\nOptional variables:")
        print("  ENVIRONMENT - development|production|test (default: development)")
        print("  FRONTEND_URL - Frontend URL for CORS (required in production)")
        print("  PORT - Server port (default: 8000)")
        print("\nGenerate a strong secret:")
        print("  openssl rand -hex 32")
        print()
        raise


# Global config instance
config: Config = load_config()


# ==============================================================================
# Usage Example
# ==============================================================================

if __name__ == "__main__":
    """
    Example usage in main.py:

    from env_validation import config

    # Use validated config
    app = FastAPI(debug=config.DEBUG)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
    )

    # Use secret
    jwt.decode(token, config.BETTER_AUTH_SECRET, algorithms=[config.JWT_ALGORITHM])
    """

    print("\n=== Configuration Summary ===")
    print(f"Environment: {config.ENVIRONMENT.value}")
    print(f"Debug: {config.DEBUG}")
    print(f"Host: {config.HOST}")
    print(f"Port: {config.PORT}")
    print(f"JWT Algorithm: {config.JWT_ALGORITHM}")
    print(f"JWT Expiration: {config.JWT_EXPIRATION_HOURS} hours")
    print(f"CORS Origins: {config.cors_origins}")
    print(f"Rate Limit: {config.RATE_LIMIT_PER_MINUTE}/min")
    print(f"Database: {config.DATABASE_URL.split('@')[1] if '@' in config.DATABASE_URL else 'configured'}")
    print()
