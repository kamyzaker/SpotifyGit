import logging
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Start, Group, Select, SwitchTo
from aiogram.enums import ContentType
from aiogram_dialog.widgets.media import DynamicMedia
from app.bot.states.states import Search_ArtistSG, MainMenuSG
from app.bot.utils.validators import track_and_album_check, no_text, error_artist_search, correct_artist_search
from app.bot.getters.search import artist_results_getter, select_album_getter, show_tracks_getter
from app.bot.keyboards.on_click_dialog import on_artist_selected, on_album_selected, send_track_preview
from app.bot.getters.i18n import get_i18n


logger = logging.getLogger(__name__)


search_artist = Dialog(
    Window(
        Format("{i18n[search_artist]}"),
        TextInput(
            id='search_artist',
            type_factory=track_and_album_check,
            on_success=correct_artist_search,
            on_error=error_artist_search,
        ),
        MessageInput(
            func=no_text,
            content_types=ContentType.ANY
        ),
        Start(Format("{i18n[back]}"), id='back_to_menu', state=MainMenuSG.menu),
        state=Search_ArtistSG.search_artist,
        getter=get_i18n,
    ),
    Window(
        Format("{i18n[list_artists]}"),
        Group(
            Select(
                Format("{item[0]}"),
                id="select_artist",
                item_id_getter=lambda x: x[1],
                items="artists",
                on_click=lambda c, w, dm, artists_idx: on_artist_selected(c, w, dm, artist_idx=artists_idx)
            ),
            width=1,
        ),
        SwitchTo(Format("{i18n[back]}"), id='back_to_menu', state=Search_ArtistSG.search_artist),
        state=Search_ArtistSG.search_artist_results,
        getter=artist_results_getter,
    ),
    Window(
        Format("{i18n[list_album_single]}: {artist_name}"),
        DynamicMedia("photo"),
        Group(
            Select(
                Format("{item[0]}"),
                id="select_album",
                item_id_getter=lambda x: x[1],
                items="albums",
                on_click=lambda c, w, dm, album_idx: on_album_selected(c, w, dm, album_idx)
            ),
            width=1,
        ),
        SwitchTo(Format("{i18n[back]}"), id='back_to_menu', state=Search_ArtistSG.search_artist_results),
        state=Search_ArtistSG.select_album,
        getter=select_album_getter,
    ),
    Window(
        Format("{i18n[album_word]}: {album_name} {i18n[artist_word]}: {performer}"),
        DynamicMedia("photo_album"),
        Group(
            Select(
                Format("{item[0]}"),
                id="select_album",
                item_id_getter=lambda x: x[1],
                items="tracks",
                on_click=lambda c, w, dm, tid: send_track_preview(c, tid, dm=dm)
            ),
            width=1,
        ),
        SwitchTo(Format("{i18n[back]}"), id='back_to_menu', state=Search_ArtistSG.select_album),
        state=Search_ArtistSG.show_tracks,
        getter=show_tracks_getter,
    ),
)
