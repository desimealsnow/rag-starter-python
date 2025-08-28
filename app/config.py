from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Which LLM provider to use
    PROVIDER: str = "ollama"  # 'ollama' | 'openai' | 'groq'

    # Ollama (local)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"

    # OpenAI (hosted)
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Groq (hosted, OpenAI-compatible)
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # Paths
    DOCS_DIR: str = "data/docs"
    INDEX_DIR: str = "data/index"

settings = Settings()
