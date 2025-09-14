import logging
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Select, Group, Start
from app.bot.states.states import MainMenuSG, TopTodaySG
from app.bot.keyboards.on_click_dialog import send_track_preview
from app.bot.getters.top_tracks import top_today_getter



logger = logging.getLogger(__name__)

top_today_dialog = Dialog(
    Window(
        Format("{i18n[top_today_dio]}"),
        Format('Ошибка: {error}', when='error'),
        Group(
            Select(
                Format('{item[0]}'),
                id='top_today_tracks',
                item_id_getter=lambda x: x[1],
                items='tracks',
                on_click=lambda c, w, dm, tid: send_track_preview(c, tid, dm=dm)
            ),
            Start(Format("{i18n[back]}"), id='back_to_menu', state=MainMenuSG.menu),
            width=1,
        ),
        state=TopTodaySG.select_track,
        getter=top_today_getter,
    )
)