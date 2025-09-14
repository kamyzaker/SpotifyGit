# from aiogram_dialog import DialogManager
# from aiogram_dialog.api.entities import MediaAttachment
# from aiogram.types import ContentType

# async def artist_results_getter(dialog_manager: DialogManager, **kwargs):
#     i18n = dialog_manager.middleware_data.get('i18n', {})
#     results_search = dialog_manager.dialog_data.get('results_search', {})
#     artists = [(f"{artist['artist_name']}", str(idx)) for idx, artist in results_search.items()]
#     return {'artists': artists}



# async def select_album_getter(dialog_manager: DialogManager, **kwargs):
#     i18n = dialog_manager.middleware_data.get('i18n', {})
#     selected_artist = dialog_manager.dialog_data.get('selected_artist', {})
#     albums = [(album['album_name'], str(idx)) for idx, album in enumerate(selected_artist.get('albums', []))]
#     image = selected_artist.get('image')
#     photo = MediaAttachment(type=ContentType.PHOTO, url=image) if image else None
#     return {'albums': albums, 'photo': photo, 'artist_name': selected_artist.get('artist_name')}


# async def show_tracks_getter(dialog_manager: DialogManager, **kwargs):
#     i18n = dialog_manager.middleware_data.get('i18n', {})
#     tracks = dialog_manager.dialog_data.get('tracks', [])
#     image_album = dialog_manager.dialog_data.get('image_album')
#     full_url = dialog_manager.dialog_data.get('full_url')
#     performer = dialog_manager.dialog_data.get('performer')
#     album_name = dialog_manager.dialog_data.get('album_name')
#     photo_album = MediaAttachment(type=ContentType.PHOTO, url=image_album) if image_album else None 
#     return {'tracks': tracks, 'photo_album': photo_album, 'full_url': full_url, 'performer': performer, 'album_name': album_name}

