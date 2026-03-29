from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGENT_API_", env_file=".env", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8765
    log_level: str = "info"

    # Чувствительность «изменения» для float (проценты / ваты)
    change_epsilon_percent: float = 0.05
    change_epsilon_watts: float = 0.5
    change_epsilon_mib: float = 1.0
    change_epsilon_temp: float = 0.5

    ollama_name_substrings: tuple[str, ...] = ("ollama",)


settings = Settings()
