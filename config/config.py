import logging
import os
from dataclasses import dataclass
from environs import Env

logger = logging.getLogger(__name__)

@dataclass
class BotSettings:
    token: str
    admin_ids: list[int]

@dataclass
class LogSettings:
    level: str
    format: str


@dataclass
class DatabaseSettings:
    name: str
    host: str
    port: int
    user: str
    password: str

@dataclass
class RedisSettings:
    host: str
    port: int
    db: int
    password: str
    username: str

@dataclass
class SpotifySettings:
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str



@dataclass
class Config:
    bot: BotSettings
    db: DatabaseSettings
    spotify: SpotifySettings 
    redis: RedisSettings
    log: LogSettings
    




def load_config(path: str | None = None) -> Config:
    env = Env()
    if path:
        if not os.path.exists(path):
            logger.warning(".env file not found at '%s' skipping...", path)
        else:
            logger.info("Loading .env file from '%s'", path) 
    env.read_env(path)

    token = env("BOT_TOKEN")
    if not token: 
        raise ValueError("BOT_TOKEN must not be empty")
    raw_ids = env.list("ADMIN_IDS", default=[])
    try:
        admin_ids = [int(admin_id) for admin_id in raw_ids]
    except ValueError as e: 
        raise ValueError("ADMIN_IDS must be a list of integers") from e
    
    log_settings = LogSettings(
        level=env("LOG_LEVEL"),
        format=env("LOG_FORMAT")
    )

    spotify = SpotifySettings(
        client_id=env("SPOTIFY_CLIENT_ID"),
        client_secret=env("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=env("SPOTIFY_REDIRECT_URI"),
        scope=env("SPOTIFY_SCOPE"),
    )
    db = DatabaseSettings(
        name=env("POSTGRES_DB"),
        host=env("POSTGRES_HOST"),
        port=env.int("POSTGRES_PORT"),
        user=env("POSTGRES_USER"),
        password=env("POSTGRES_PASSWORD"),
    )

    redis = RedisSettings(
        host=env("REDIS_HOST"),
        port=env.int("REDIS_PORT"),
        db=env.int("REDIS_DATABASE"),
        password=env("REDIS_PASSWORD", default=""),
        username=env("REDIS_USERNAME", default=""),
    )


    logger.info("Configuration loaded successfully")
    
    return Config(
        bot=BotSettings(token=token, admin_ids=admin_ids),
        db=db,
        redis=redis,
        spotify=spotify,     
        log=log_settings,
    )