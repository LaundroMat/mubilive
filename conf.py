from pydantic import BaseSettings


class Settings(BaseSettings):
    twitter_api_key: str
    twitter_api_secret: str

    twitter_access_token: str
    twitter_access_token_secret: str

    fauna_db_key: str

    test: bool = False

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
