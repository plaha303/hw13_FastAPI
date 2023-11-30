from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_name: str
    postgres_domain: str
    postgres_port: int
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    redis_host: str
    redis_port: int

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
