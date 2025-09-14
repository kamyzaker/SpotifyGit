import logging

import psycopg_pool
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_dialog import setup_dialogs
from config.config import Config
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from redis.asyncio import Redis
from app.infrastructure.database.connection import get_pg_pool
from app.bot.i18n.translator import get_translations
from app.bot.handlers.auth import router_start
from app.bot.handlers.callbacks import router_callback
from app.bot.handlers.settings import settings_router
from app.bot.handlers.admin import admin_router
from app.bot.dialogs.main_menu import main_menu_dialog
from app.bot.dialogs.search_track import search_track_dialog
from app.bot.dialogs.search_album import search_album_dialog
from app.bot.dialogs.top_all_time import top_all_time_dialog
from app.bot.dialogs.top_today import top_today_dialog
from app.bot.dialogs.search_artist import search_artist
from app.bot.middlewares.database import DataBaseMiddleware
from app.bot.middlewares.i18n import TranslatorMiddleware
from app.bot.middlewares.lang_settings import LangSettingsMiddleware
from app.bot.middlewares.shadow_ban import ShadowBanMiddleware
from app.bot.middlewares.statistics import ActivityCounterMiddleware
from config.config import load_config

logger = logging.getLogger(__name__)
config = load_config()  
storage = RedisStorage(
    redis=Redis(
        host=config.redis.host,
        port=config.redis.port,
        db=config.redis.db,
        password=config.redis.password,
        username=config.redis.username,
    ),
    key_builder=DefaultKeyBuilder(with_destiny=True)
)
logger.info("Storage initialized globally as RedisStorage")


async def main() -> None:
    logger.info("Starting bot...")

    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)
    db_pool: psycopg_pool.AsyncConnectionPool = await get_pg_pool(
        db_name=config.db.name,
        host=config.db.host,
        port=config.db.port,
        user=config.db.user,
        password=config.db.password,
    )
    translations = get_translations()
    locales = list(translations.keys())
    logger.info("Including routers...")
    dp.include_routers(router_start, admin_router, router_callback, settings_router)

    logger.info("Including dialogs...")
    dp.include_routers(main_menu_dialog, search_track_dialog, search_album_dialog, top_all_time_dialog, top_today_dialog, search_artist)
    setup_dialogs(dp)

    logger.info("Including middlewares...")
    dp.update.middleware(DataBaseMiddleware())
    dp.update.middleware(ShadowBanMiddleware())
    dp.update.middleware(ActivityCounterMiddleware())
    dp.update.middleware(LangSettingsMiddleware())
    dp.update.middleware(TranslatorMiddleware())



    try:
        await dp.start_polling(
            bot, 
            db_pool=db_pool,
            translations=translations,
            locales=locales,
            admin_ids=config.bot.admin_ids,
        )
    except Exception as e:
        logger.exception(e)
    
