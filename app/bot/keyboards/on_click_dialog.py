import spotipy

from aiogram_dialog import DialogManager
from aiogram_dialog import DialogManager
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from app.bot.utils.spotify_utils import refresh_access_token
from app.bot.states.states import Search_ArtistSG




async def on_artist_selected(callback, widget, dialog_manager: DialogManager, artist_idx: str):
    results_search = dialog_manager.dialog_data.get('results_search', {})
    artist = results_search.get(artist_idx)
    if artist:
        dialog_manager.dialog_data['selected_artist'] = artist
        await dialog_manager.switch_to(Search_ArtistSG.select_album)



async def on_album_selected(callback, widget, dialog_manager: DialogManager, album_idx: str):
    selected_artist = dialog_manager.dialog_data.get('selected_artist', {})
    album = selected_artist.get('albums', [])[int(album_idx)]
    dialog_manager.dialog_data.update(
        tracks=album['tracks'],
        image_album=album['image'],
        full_url=album['url'],
        performer=selected_artist['artist_name'],
        album_name=album['album_name']
    )
    await dialog_manager.switch_to(Search_ArtistSG.show_tracks)




async def send_track_preview(message_or_callback, track_id, state: FSMContext = None, dm: DialogManager = None):
    if state is None and dm is not None:
        try:
            chat_id = dm.event.message.chat.id if hasattr(dm.event, 'message') and dm.event.message else dm.event.from_user.id
            state_key = StorageKey(
                bot_id=dm.event.bot.id,
                chat_id=chat_id,
                user_id=dm.event.from_user.id
            )
            from app.bot.bot import storage
            state = FSMContext(storage=storage, key=state_key)
        except Exception as e:
            await message_or_callback.answer(f'Ошибка получения состояния: {str(e)}')
            return

    if state is None:
        await message_or_callback.answer('Ошибка: Нет доступа к состоянию!')
        return

    data = await state.get_data()
    access_token = data.get('access_token')

    sp = spotipy.Spotify(auth=access_token)
    try:
        track = sp.track(track_id, market="US")
        preview_url = track['preview_url']
        full_url = track['external_urls']['spotify']
        title = track['name']
        performer = track['artists'][0]['name']
        kb = InlineKeyboardMarkup(
                inline_keyboard=[
                [InlineKeyboardButton(text=('◀️ Назад'), callback_data='back_to_list')]
                ]
            )

        if preview_url:
            if isinstance(message_or_callback, CallbackQuery):
                sent_message = await message_or_callback.message.answer_audio(
                    audio=preview_url,
                    title=title,
                    performer=performer,
                    caption=f'Preview (30 сек): {title} by {performer}. Полный: {full_url}',
                    reply_markup=kb
                )
            else:
                sent_message = await message_or_callback.answer_audio(
                    audio=preview_url,
                    title=title,
                    performer=performer,
                    caption=f'Preview (30 сек): {title} by {performer}. Полный: {full_url}',
                    reply_markup=kb
                )
        else:
            if isinstance(message_or_callback, CallbackQuery) and dm:
                sent_message = await message_or_callback.message.answer(text=f'Сниппет не найден. Полный трек: {full_url}', reply_markup=kb)
            else:
                sent_message = await message_or_callback.answer(text=f'Сниппет не найден. Полный трек: {full_url}', reply_markup=kb)

        if dm:
            dm.dialog_data['preview_message_id'] = sent_message.message_id
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 401:
            new_token = await refresh_access_token(state)
            if new_token:
                await send_track_preview(message_or_callback, track_id, state=state, dm=dm)
            else:
                await message_or_callback.answer(f'Токен истёк. Авторизуйся заново.')
        else:
            await message_or_callback.answer(f'Ошибка: {str(e)}')
    except Exception as e:
        await message_or_callback.answer(f'Ошибка: {str(e)}')
