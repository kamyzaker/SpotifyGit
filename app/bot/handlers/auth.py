import logging
from contextlib import suppress

from psycopg.connection_async import AsyncConnection
from aiogram import Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command, ChatMemberUpdatedFilter, KICKED
from aiogram.enums import BotCommandScopeType
from aiogram.types import BotCommandScopeChat,  Message, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberUpdated
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, StartMode
from app.bot.enums.roles import UserRole
from app.bot.states.states import SpotifyAuthSG, MainMenuSG, LangSG
from app.bot.utils.spotify_utils import get_spotify_oauth
from app.bot.keyboards.menu_button import get_main_menu_commands
from app.infrastructure.database.db import(
    add_user,
    change_user_alive_status,
    get_user,
    get_user_lang,
    get_user_spotify_status,
    change_auth_on_spotify_status
)

logger = logging.getLogger(__name__)
router_start = Router()


@router_start.message(CommandStart())
async def process_start_command(
    message: Message,
    conn: AsyncConnection,
    bot: Bot,
    i18n: dict[str, str],
    state: FSMContext,
    admin_ids: list[int],
    translations: dict,
    dialog_manager: DialogManager
):
    user_row = await get_user(conn, user_id=message.from_user.id)
    if user_row is None:
        if message.from_user.id in admin_ids:
            role = UserRole.ADMIN
        else:
            role = UserRole.USER
        await add_user(
            conn, 
            user_id=message.from_user.id, 
            username=message.from_user.username,
            language=message.from_user.language_code,
            role=role
            )
        user_role = role
    else:
        user_role = UserRole(user_row[4])
        await change_user_alive_status(
            conn,
            is_alive=True,
            user_id=message.from_user.id)
    data = await state.get_data()
    if await state.get_state() == LangSG.lang:
        with suppress(TelegramBadRequest):
            msg_id = data.get("lang_settings_msg_id")
            if msg_id:
                await bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=msg_id)
        user_lang = await get_user_lang(conn, user_id=message.from_user.id)
        i18n = translations.get(user_lang)

    await bot.set_my_commands(
        commands=get_main_menu_commands(i18n=i18n, role=user_role),
        scope=BotCommandScopeChat(
            type=BotCommandScopeType.CHAT,
            chat_id=message.from_user.id
        )
    )
    auth_spotifu_status = await get_user_spotify_status(conn, user_id=message.from_user.id)
    logger.info(f"data: {data}")
    if auth_spotifu_status is False or data.get("access_token") is None:
        oauth = get_spotify_oauth()
        auth_url = oauth.get_authorize_url()
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=i18n.get("auth_button"), url=auth_url)]
            ]
        )
        await message.answer(text=i18n.get("/start"))
        await message.answer(i18n.get("auth_spotify"), reply_markup=kb)
        await state.set_state(SpotifyAuthSG.waiting_for_code)
    else:
        logger.info(f"Stack size: {len(dialog_manager.s)}")
        await dialog_manager.start(state=MainMenuSG.menu, mode=StartMode.RESET_STACK)
        
    





@router_start.message(SpotifyAuthSG.waiting_for_code)
async def process_code(message: Message, conn: AsyncConnection, state: FSMContext, dialog_manager: DialogManager, i18n: dict[str, str]):
    redirect_url = message.text.strip()
    try:
        oauth = get_spotify_oauth()
        code = oauth.parse_response_code(redirect_url)
        token_info = oauth.get_access_token(code)
        access_token = token_info['access_token'] 
        refresh_token = token_info.get('refresh_token') 

        await state.update_data(access_token=access_token, refresh_token=refresh_token)
        await change_auth_on_spotify_status(conn, auth_on_spotify=True, user_id=message.from_user.id)
        await message.answer(i18n.get("success"))
        await state.set_state()


        await dialog_manager.start(state=MainMenuSG.menu, data={'access_token': access_token})
        dialog_manager.dialog_data['access_token'] = access_token   
    except Exception as e:
        await message.answer(f'Ошибка: {str(e)}. Попробуй заново.')



@router_start.message(Command(commands="help"))
async def process_help_command(message: Message, i18n: dict[str, str], state: FSMContext, dialog_manager: DialogManager):
    await dialog_manager.start(state=MainMenuSG.menu)
    await message.answer(text=i18n.get("/help"))


# Этот хэндлер будет срабатывать на блокировку бота пользователем
@router_start.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def process_user_blocked_bot(event: ChatMemberUpdated, conn: AsyncConnection):
    logger.info("User %d has blocked the bot", event.from_user.id)
    await change_user_alive_status(conn, user_id=event.from_user.id, is_alive=False)