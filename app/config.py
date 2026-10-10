from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int


    OLLAMA_HOST: str

    EMBED_MODEL: str
    LLM_MODEL: str


    

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
        )

settings = Settings()
