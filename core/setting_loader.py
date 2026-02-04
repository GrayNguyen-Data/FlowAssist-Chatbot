from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

CONFIG_PATH = BASE_DIR / "config" / "settings.yaml"


def load_settings():
    # Load YAML settings
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        settings = yaml.safe_load(file)

    # ===== Application Configuration =====
    if os.getenv("APP_ENV"):
        settings["app"]["env"] = os.getenv("APP_ENV")
    if os.getenv("LOG_LEVEL"):
        settings["app"]["log_level"] = os.getenv("LOG_LEVEL")
    
    # ===== Vector Database (TiDB) Configuration =====
    if os.getenv("TIDB_HOST"):
        settings["vector_store"]["host"] = os.getenv("TIDB_HOST")
    if os.getenv("TIDB_PORT"):
        settings["vector_store"]["port"] = int(os.getenv("TIDB_PORT"))
    if os.getenv("TIDB_USER"):
        settings["vector_store"]["user"] = os.getenv("TIDB_USER")
    if os.getenv("TIDB_PASSWORD"):
        settings["vector_store"]["password"] = os.getenv("TIDB_PASSWORD")
    if os.getenv("TIDB_DATABASE"):
        settings["vector_store"]["database"] = os.getenv("TIDB_DATABASE")
    if os.getenv("TIDB_TABLE"):
        settings["vector_store"]["table"] = os.getenv("TIDB_TABLE")
    if os.getenv("TIDB_DISTANCE"):
        settings["vector_store"]["distance"] = os.getenv("TIDB_DISTANCE")
    if os.getenv("TIDB_TIMEOUT"):
        settings["vector_store"]["timeout"] = int(os.getenv("TIDB_TIMEOUT"))
    
    # ===== Embedding Model Configuration =====
    if os.getenv("EMBEDDING_MODEL"):
        settings["embedding"]["model"] = os.getenv("EMBEDDING_MODEL")
    if os.getenv("EMBEDDING_VECTOR_SIZE"):
        settings["embedding"]["vector_size"] = int(os.getenv("EMBEDDING_VECTOR_SIZE"))
    if os.getenv("EMBEDDING_DEVICE"):
        settings["embedding"]["device"] = os.getenv("EMBEDDING_DEVICE")
    if os.getenv("EMBEDDING_BATCH_SIZE"):
        settings["embedding"]["batch_size"] = int(os.getenv("EMBEDDING_BATCH_SIZE"))
    
    # ===== LLM Configuration =====
    if os.getenv("LLM_PROVIDER"):
        settings["llm"]["provider"] = os.getenv("LLM_PROVIDER")
    if os.getenv("LLM_MODEL_NAME"):
        settings["llm"]["model_name"] = os.getenv("LLM_MODEL_NAME")
    if os.getenv("LLM_BASE_URL"):
        settings["llm"]["base_url"] = os.getenv("LLM_BASE_URL")
    if os.getenv("LLM_TEMPERATURE"):
        settings["llm"]["temperature"] = float(os.getenv("LLM_TEMPERATURE"))
    if os.getenv("LLM_MAX_TOKENS"):
        settings["llm"]["max_tokens"] = int(os.getenv("LLM_MAX_TOKENS"))
    if os.getenv("LLM_TIMEOUT"):
        settings["llm"]["timeout"] = int(os.getenv("LLM_TIMEOUT"))
    
    # ===== Retrieval Configuration =====
    if os.getenv("RETRIEVAL_TOP_K"):
        settings["retrieval"]["top_k"] = int(os.getenv("RETRIEVAL_TOP_K"))
    if os.getenv("RETRIEVAL_SCORE_THRESHOLD"):
        settings["retrieval"]["score_threshold"] = float(os.getenv("RETRIEVAL_SCORE_THRESHOLD"))
    
    # ===== Data Configuration =====
    if os.getenv("CHUNKING_SIZE"):
        settings["chunking"]["chunking_size"] = int(os.getenv("CHUNKING_SIZE"))
    if os.getenv("CHUNKING_OVERLAP"):
        settings["chunking"]["overlap_size"] = int(os.getenv("CHUNKING_OVERLAP"))
    
    # ===== Security Configuration =====
    if os.getenv("MAX_QUERY_LENGTH"):
        settings["security"]["max_query_length"] = int(os.getenv("MAX_QUERY_LENGTH"))
    if os.getenv("RATE_LIMIT_PER_MINUTE"):
        settings["security"]["rate_limit_per_minute"] = int(os.getenv("RATE_LIMIT_PER_MINUTE"))

    # ===== MinIO Configuration =====
    if os.getenv("MINIO_ROOT_USER"):
        settings["minio"]["minio_username"] = os.getenv("MINIO_ROOT_USER")
    if os.getenv("MINIO_ROOT_PASSWORD"):
        settings["minio"]["minio_password"] = os.getenv("MINIO_ROOT_PASSWORD")
    if os.getenv("MINIO_ENDPOINT"):
        settings["minio"]["minio_endpoint"] = os.getenv("MINIO_ENDPOINT")
    if os.getenv("MINIO_BUCKET_NAME"):
        settings["minio"]["minio_bucket_name"] = os.getenv("MINIO_BUCKET_NAME")
    
    # ===== Config Groq =====
    if os.getenv("API_KEY_GROQ"):
        settings['groq']['groq_api_key'] = os.getenv("API_KEY_GROQ")
    
    return settings


