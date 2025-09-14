import logging
from aiogram_dialog import DialogManager
from aiogram.types import ContentType
from aiogram_dialog.api.entities import MediaAttachment
from app.bot.states.states import SearchSG, Search_AlbumSG

logger = logging.getLogger(__name__)


async def search_track_getter(dialog_manager: DialogManager, **kwargs):
    i18n = dialog_manager.middleware_data.get('i18n', {})
    dialog_manager.dialog_data['previous_state'] = SearchSG.search_track.state
    return {"i18n": i18n}




async def search_album_getter(dialog_manager: DialogManager, **kwargs):
    i18n = dialog_manager.middleware_data.get('i18n', {})
    dialog_manager.dialog_data['previous_state'] = Search_AlbumSG.search_album_2.state
    tracks = dialog_manager.dialog_data.get("tracks", [])
    image_album = dialog_manager.dialog_data.get("image_album")
    full_url = dialog_manager.dialog_data.get("full_url")
    performer = dialog_manager.dialog_data.get("performer", "Неизвестный исполнитель") 
    album_name = dialog_manager.dialog_data.get("album_name", "Неизвестный альбом")
    photo_album = MediaAttachment(type=ContentType.PHOTO, url=image_album) if image_album else ""
    return {"i18n": i18n, "tracks": tracks, "photo_album": photo_album, "full_url": full_url, "performer": performer, "album_name": album_name}




async def artist_results_getter(dialog_manager: DialogManager, **kwargs):
    i18n = dialog_manager.middleware_data.get('i18n', {})
    results_search = dialog_manager.dialog_data.get('results_search', {})
    artists = [(f"{artist['artist_name']}", str(idx)) for idx, artist in results_search.items()]
    return {"i18n": i18n, 'artists': artists}


async def select_album_getter(dialog_manager: DialogManager, **kwargs):
    i18n = dialog_manager.middleware_data.get('i18n', {})
    selected_artist = dialog_manager.dialog_data.get('selected_artist', {})
    albums = [(album['album_name'], str(idx)) for idx, album in enumerate(selected_artist.get('albums', []))]
    image = selected_artist.get('image')
    photo = MediaAttachment(type=ContentType.PHOTO, url=image) if image else None
    return {"i18n": i18n,'albums': albums, 'photo': photo, 'artist_name': selected_artist.get('artist_name')}


async def show_tracks_getter(dialog_manager: DialogManager, **kwargs):
    i18n = dialog_manager.middleware_data.get('i18n', {})
    tracks = dialog_manager.dialog_data.get('tracks', [])
    image_album = dialog_manager.dialog_data.get('image_album')
    full_url = dialog_manager.dialog_data.get('full_url')
    performer = dialog_manager.dialog_data.get('performer')
    album_name = dialog_manager.dialog_data.get('album_name')
    photo_album = MediaAttachment(type=ContentType.PHOTO, url=image_album) if image_album else None 
    return {"i18n": i18n,'tracks': tracks, 'photo_album': photo_album, 'full_url': full_url, 'performer': performer, 'album_name': album_name}
