import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Casbin RBAC"
    API_PREFIX: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-placeholder")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # RBAC settings
    CASBIN_MODEL_PATH: str = "rbac_model.conf"
    CASBIN_POLICY_PATH: str = "policy.csv"
    
    class Config:
        env_file = ".env"

settings = Settings()