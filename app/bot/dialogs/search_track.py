import logging
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Start
from aiogram.enums import ContentType
from app.bot.states.states import MainMenuSG, SearchSG
from app.bot.utils.validators import track_and_album_check, no_text, correct_track_search, error_track_search
from app.bot.getters.search import search_track_getter



logger = logging.getLogger(__name__)


search_track_dialog = Dialog(
    Window(
        Format("{i18n[search_track_artist]}"),
        TextInput(
            id='search_track',
            type_factory=track_and_album_check,
            on_success=correct_track_search,
            on_error=error_track_search,
        ),
        MessageInput(
            func=no_text,
            content_types=ContentType.ANY
        ),
        Start(Format("{i18n[back]}"), id='back_to_menu', state=MainMenuSG.menu),
        state=SearchSG.search_track,
        getter=search_track_getter,
    )
)