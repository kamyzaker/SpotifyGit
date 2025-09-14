from aiogram.fsm.state import StatesGroup, State

class SpotifyAuthSG(StatesGroup):
    waiting_for_code = State()

class MainMenuSG(StatesGroup):
    menu = State()

class TopTodaySG(StatesGroup):
    select_track = State()

class TopAllTimeSG(StatesGroup):
    select_track = State()

class SearchSG(StatesGroup):
    search_track = State()

class Search_AlbumSG(StatesGroup):
    search_album_1 = State()
    search_album_2 = State()

class Search_ArtistSG(StatesGroup):
    search_artist = State()  # Ввод имени артиста
    search_artist_results = State()  # Выбор артиста
    select_album = State()  # Выбор альбома
    show_tracks = State()  # Показ треков
    
class LangSG(StatesGroup):
    lang = State()