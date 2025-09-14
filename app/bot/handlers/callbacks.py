import logging
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram import Router
from app.bot.states.states import SearchSG, Search_AlbumSG

logger = logging.getLogger(__name__)
router_callback = Router()

@router_callback.callback_query(F.data == 'back_to_list')
async def back_to_list_callback(callback: CallbackQuery, dialog_manager: DialogManager):
    preview_message_id = dialog_manager.dialog_data.get('preview_message_id')
    try:
        await callback.bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=preview_message_id
        )
        dialog_manager.dialog_data.pop('preview_message_id', None)
        return
    except Exception as e:
        logger.info(f"Ошибка удаления сообщения: {str(e)}")
    
    previous_state = dialog_manager.dialog_data.get('previous_state')
    

    state_map = {
        'SearchSG.search_track': SearchSG.search_track,
        'Search_AlbumSG.search_album_2': Search_AlbumSG.search_album_2,

    }
    
    if previous_state and previous_state != 'SearchSG.search_track':  
        state_obj = state_map.get(previous_state)  # Конвертируем строку в объект State
        if state_obj:
            await dialog_manager.switch_to(state_obj)
            logger.info("Вернулись в предыдущий диалог: %s", previous_state)
        else:
            logger.warning("Неизвестное состояние: %s", previous_state)
            await dialog_manager.done() 
    else: 
        await dialog_manager.done()

    
    await callback.answer()