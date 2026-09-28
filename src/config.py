import pathlib

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{pathlib.Path(__file__).parents[1]}/.env",
        extra="ignore",
        case_sensitive=False,
        env_nested_delimiter="__",
    )

    db_host: str
    db_port: str | int
    db_database: str
    db_user: str
    db_pass: str

    @property
    def postgres_url(self):
        url = (
            f"postgresql+asyncpg://{self.db_user}:"
            f"{self.db_pass}@{self.db_host}:"
            f"{self.db_port}/{self.db_database}"
        )
        return url


settings = Settings()
