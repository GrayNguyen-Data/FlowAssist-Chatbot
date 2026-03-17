from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "FlowAssist Chatbot"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "local"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = True

    API_PREFIX: str = "/api/v1"

    DATA_RAW_DIR: str = "data" 
    DATA_PROCESSED_DIR: str = "data/processed_data"
    DATA_SCHEMA_DIR: str = "data/schema"

    CHUNKING_SIZE: int = 500
    CHUNKING_OVERLAP: int = 50

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_VECTOR_SIZE: int = 384
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_DEVICE: str = "cpu"

    TIDB_HOST: str
    TIDB_PORT: int = 4000
    TIDB_USER: str
    TIDB_PASSWORD: str
    TIDB_DATABASE: str
    TIDB_CA_PATH: str | None = None
    TIDB_TABLE: str = "rag_embeddings"
    TIDB_DISTANCE: str = "cosine"
    TIDB_TIMEOUT: int = 10

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    REDIS_MEMORY_TTL_SECONDS: int = 3600
    REDIS_MAX_MEMORY_MESSAGES: int = 10

    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_SCORE_THRESHOLD: float = 0.0

    LLM_PROVIDER: str = "groq"
    LLM_MODEL_NAME: str = "llama-3.1-8b-instant"
    LLM_BASE_URL: str | None = None
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int | None = None
    LLM_TIMEOUT: int = 60

    GROQ_API_KEY: str

    MAX_QUERY_LENGTH: int = 2000
    RATE_LIMIT_PER_MINUTE: int = 60

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_RAW_BUCKET_NAME: str = "raw-data"
    MINIO_PROCESSED_BUCKET_NAME: str = "processed-data"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()