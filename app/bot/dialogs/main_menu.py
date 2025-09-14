import logging
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.text import Format
from app.bot.states.states import MainMenuSG, TopTodaySG, TopAllTimeSG, SearchSG, Search_AlbumSG, Search_ArtistSG
from app.bot.getters.i18n import get_i18n

logger = logging.getLogger(__name__)

main_menu_dialog = Dialog(
    Window(
        Format("{i18n[main_menu]}"),
        Group(
            Button(Format("{i18n[top_today_button]}"), id='top_today', on_click=lambda c, b, dm: dm.start(TopTodaySG.select_track, data=dm.dialog_data)),
            Button(Format("{i18n[top_alltime_button]}"), id='top_all_time', on_click=lambda c, b, dm: dm.start(TopAllTimeSG.select_track, data=dm.dialog_data)),
            Button(Format("{i18n[search_track]}"), id='search_track', on_click=lambda c, b, dm: dm.start(SearchSG.search_track, data=dm.dialog_data)),
            Button(Format("{i18n[search_album]}"), id='search_album', on_click=lambda c, b, dm: dm.start(Search_AlbumSG.search_album_1, data=dm.dialog_data)),
            Button(Format("{i18n[search_artist]}"), id='search_artist', on_click=lambda c, b, dm: dm.start(Search_ArtistSG.search_artist, data=dm.dialog_data)),
            width=1,
        ),
        state=MainMenuSG.menu,
        getter=get_i18n
    )
)