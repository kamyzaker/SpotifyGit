import logging
import spotipy
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager
from aiogram.fsm.storage.base import StorageKey
from app.bot.states.states import TopTodaySG, TopAllTimeSG
from app.bot.utils.spotify_utils import refresh_access_token

logger = logging.getLogger(__name__)




async def top_tracks_getter(dialog_manager: DialogManager, playlist_id: str, **kwargs):
    i18n = dialog_manager.middleware_data.get('i18n', {})
    try:
        state_key = StorageKey(
            bot_id=dialog_manager.event.bot.id,
            chat_id=dialog_manager.event.message.chat.id,
            user_id=dialog_manager.event.from_user.id
        )
        from app.bot.bot import storage
        state = FSMContext(storage=storage, key=state_key)
    except Exception as e:
        logger.info(f"Ошибка получения состояния: {str(e)}")
        return {'tracks': [], 'error': 'Ошибка получения состояния'}
    data = await state.get_data()
    access_token = data.get('access_token')
    try:
        sp = spotipy.Spotify(auth=access_token)
        results = sp.playlist_tracks(playlist_id, limit=50)
        if 'items' not in results or results['items'] is None:
            raise ValueError("Пустой результат от API")
        tracks = [(f"{track['track']['name']} - {track['track']['artists'][0]['name']}", track['track']['id']) for track in results['items']]
        return {'i18n': i18n, 'tracks': tracks}
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 401:
            new_token = await refresh_access_token(state)
            if new_token:
                return await top_tracks_getter(dialog_manager, playlist_id, **kwargs)
        return {'tracks': [], 'error': str(e)}
    except Exception as e:
        return {'tracks': [], 'error': str(e)}

async def top_today_getter(dialog_manager: DialogManager, **kwargs):
    dialog_manager.dialog_data['previous_state'] = TopTodaySG.select_track.state
    return await top_tracks_getter(dialog_manager, playlist_id='5ABHKGoOzxkaa28ttQV9sE', **kwargs)

async def top_all_time_getter(dialog_manager: DialogManager, **kwargs):
    dialog_manager.dialog_data['previous_state'] = TopAllTimeSG.select_track.state
    return await top_tracks_getter(dialog_manager, playlist_id='5ABHKGoOzxkaa28ttQV9sE', **kwargs)