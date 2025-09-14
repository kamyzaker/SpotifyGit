from spotipy.oauth2 import SpotifyOAuth
from aiogram.fsm.context import FSMContext
from config.config import Config, load_config


config: Config = load_config()


def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=config.spotify.client_id,
        client_secret=config.spotify.client_secret,
        redirect_uri=config.spotify.redirect_uri,
        scope=config.spotify.scope,
    )

async def refresh_access_token(state: FSMContext):
    data = await state.get_data()
    refresh_token = data.get('refresh_token') 
    if not refresh_token:  
        return None
    oauth = get_spotify_oauth()
    token_info = oauth.refresh_access_token(refresh_token)
    access_token = token_info['access_token'] 
    await state.update_data(access_token=access_token)
    return access_token



