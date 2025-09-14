import logging
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import  Group
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Start
from aiogram.enums import ContentType
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.kbd import Select
from app.bot.states.states import MainMenuSG, Search_AlbumSG
from app.bot.keyboards.on_click_dialog import send_track_preview
from app.bot.getters.search import search_album_getter
from app.bot.utils.validators import track_and_album_check, correct_album_search, error_album_search, no_text
from app.bot.getters.i18n import get_i18n

logger = logging.getLogger(__name__)


search_album_dialog = Dialog(
    Window(
        Format("{i18n[search_album_dio]}"),
        TextInput(
            id='search_album',
            type_factory=track_and_album_check,
            on_success=correct_album_search,
            on_error=error_album_search,
        ),
        MessageInput(
            func=no_text,
            content_types=ContentType.ANY
        ),
        Start(Format("{i18n[back]}"), id='back_to_menu', state=MainMenuSG.menu),
        state=Search_AlbumSG.search_album_1,
        getter=get_i18n,
    ),
    Window(
        Format("{i18n[album_word]}: {performer}: {album_name}"),
        DynamicMedia("photo_album"),
        Group(
            Select(
                Format('{item[0]}'),
                id='tracks_album',
                item_id_getter=lambda x: x[1],
                items='tracks',
                on_click=lambda c, w, dm, tid: send_track_preview(c, tid, dm=dm)
            ),
            Start(Format("{i18n[back]}"), id='back_to_menu', state=MainMenuSG.menu),
            width=1,
        ),
        state=Search_AlbumSG.search_album_2,
        getter=search_album_getter,
    )
)