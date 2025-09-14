import logging

import spotipy
from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput,  ManagedTextInput
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from typing import Any
from app.bot.states.states import Search_AlbumSG, Search_ArtistSG
from app.bot.keyboards.on_click_dialog import send_track_preview
from app.bot.utils.spotify_utils import refresh_access_token

logger = logging.getLogger(__name__)




def track_and_album_check(text: Any):
    if len(text) < 30:
        return text
    raise ValueError("Слишком длинный текст для поиска. Максимум 30 символов.")

async def correct_track_search(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    from app.bot.bot import storage
    try:
        state_key = StorageKey(bot_id=message.bot.id, chat_id=message.chat.id, user_id=message.from_user.id)
        state = FSMContext(storage=storage, key=state_key)
        data = await state.get_data()
        access_token = data.get('access_token') 
        if not access_token:
            await message.answer('Сначала авторизуйся в Spotify!')
            return

        sp = spotipy.Spotify(auth=access_token)
        results = sp.search(q=text, type='track', limit=1)
        if results['tracks']['items']:
            track_id = results['tracks']['items'][0]['id']
            dialog_manager.show_mode = ShowMode.NO_UPDATE
            await send_track_preview(message, track_id, state=state)
        else:
            await message.answer('Ничего не найдено. Попробуй точнее!')
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 401:
            new_token = await refresh_access_token(state)
            if new_token:
                await correct_track_search(message, text, dialog_manager=dialog_manager)
            else:
                await message.answer(f'Токен истёк. Авторизуйся заново.')
        else:
            await message.answer(f'Ошибка: {str(e)}') 
    except Exception as e:
        await message.answer(f'Ошибка поиска: {str(e)}')

async def correct_album_search(message: Message, 
        widget: ManagedTextInput, 
        dialog_manager: DialogManager, 
        text: str) -> None:
    from app.bot.bot import storage
    try:
        state_key = StorageKey(bot_id=message.bot.id, chat_id=message.chat.id, user_id=message.from_user.id)
        state = FSMContext(storage=storage, key=state_key)
        data = await state.get_data()
        access_token = data.get('access_token')
        if not access_token:
            await message.answer('Сначала авторизуйся в Spotify!')
            return

        sp = spotipy.Spotify(auth=access_token)
        results = sp.search(q=text, type='album', limit=1, market="US")
        if results['albums']['items']:
            album = results['albums']['items'][0]
            album_id = album['id']
            image_album = album['images'][0]['url'] if album.get('images') and len(album['images']) > 0 else None
            full_url = album['external_urls']['spotify']
            album_name = album['name']
            performer = album['artists'][0]['name'] if album.get('artists') and len(album['artists']) > 0 else "Неизвестный исполнитель"  
            tracks = []
            album_tracks = sp.album_tracks(album_id, limit=50, market="US")
            for track in album_tracks['items']:
                performers = [artist['name'] for artist in track['artists']]
                track_name = track['name']
                track_id = track['id']
                tracks.append((f"{', '.join(performers)} - {track_name}", track_id))
            if tracks:
                dialog_manager.dialog_data.update(tracks=tracks, image_album=image_album, full_url=full_url, performer=performer, album_name=album_name)
                await dialog_manager.switch_to(state=Search_AlbumSG.search_album_2)
            else:
                await message.answer("В альбоме нет треков для отображения.")
        else:
            await message.answer("По вашему запросу не найдено ни одного альбома")
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 401:
            new_token = await refresh_access_token(state)
            if new_token:
                await correct_album_search(message, text, dialog_manager=dialog_manager)
            else:
                await message.answer(f'Токен истёк. Авторизуйся заново.')
        else:
            await message.answer(f'Ошибка: {str(e)}') 
    except Exception as e:
        await message.answer(f'Ошибка: {str(e)}')



async def correct_artist_search(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    from app.bot.bot import storage
    try:
        state_key = StorageKey(bot_id=message.bot.id, chat_id=message.chat.id, user_id=message.from_user.id)
        state = FSMContext(storage=storage, key=state_key)
        data = await state.get_data()
        access_token = data.get('access_token')
        if not access_token:
            await message.answer('Сначала авторизуйся в Spotify!')
            return
        

        sp = spotipy.Spotify(auth=access_token)
        results = sp.search(q=text, type='artist', limit=5, market="US")
        if not results['artists']['items']:
            await message.answer("По вашему запросу не найдено ни одного артиста")
            return

        results_search = {}
        index = 1 

        for artist in results['artists']['items']:
            artist_name = artist['name']
            artist_id = artist['id']
            image = artist['images'][0]['url'] if artist.get('images') and len(artist['images']) > 0 else None
            full_url = artist['external_urls']['spotify']
            
           
            albums = sp.artist_albums(artist_id, album_type='album,single', limit=10)
            album_data = []

            for album in albums['items']:
                album_name = album['name']
                album_id = album['id']
                album_image = album['images'][0]['url'] if album.get('images') and len(album['images']) > 0 else None
                album_url = album['external_urls']['spotify']
                
                
                tracks = []
                album_tracks = sp.album_tracks(album_id, limit=50, market="US")
                for track in album_tracks['items']:
                    track_name = track['name']
                    track_id = track['id']
                    performers = [artist['name'] for artist in track['artists']]
                    tracks.append((f"{', '.join(performers)} - {track_name}", track_id))

                if tracks:  # Добавляем альбом только если есть треки
                    album_data.append({
                        'album_name': album_name,
                        'album_id': album_id,
                        'image': album_image,
                        'url': album_url,
                        'tracks': tracks
                    })

            if album_data:  # Сохраняем только если есть альбомы с треками
                results_search[str(index)] = {
                    'artist_name': artist_name,
                    'artist_id': artist_id,
                    'image': image,
                    'url': full_url,
                    'albums': album_data
                }
                index += 1

        

        if not results_search:
            await message.answer("У найденных артистов нет альбомов или треков")
            return


        dialog_manager.dialog_data['results_search'] = results_search
        await dialog_manager.switch_to(state=Search_ArtistSG.search_artist_results) 
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 401:
            new_token = await refresh_access_token(state)
            if new_token:
                await correct_artist_search(message, text, dialog_manager=dialog_manager)
            else:
                await message.answer(f'Токен истёк. Авторизуйся заново.')
        else:
            await message.answer(f'Ошибка: {str(e)}')    
    except Exception as e:
        await message.answer(f'Ошибка: {str(e)}')



async def error_track_search(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError):
    await message.answer(
        text='Вы ввели некорректный текст. Пожалуйста, введите название трека или исполнителя (до 30 символов).',
    )

async def error_artist_search(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError):
    await message.answer(
        text='Вы ввели некорректный текст. Пожалуйста, введите корректное название исполнителя (до 30 символов).',
    )    

async def error_album_search(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError):
    await message.answer(
        text='Вы ввели некорректный текст. Пожалуйста, введите название альбома (до 30 символов).',
    )

async def no_text(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    if message.content_type != ContentType.TEXT:
        await message.answer(text='Вы отправили не текст! Введите название трека или исполнителя.')
    else:
        await message.answer(text='Вы ввели пустой текст!')