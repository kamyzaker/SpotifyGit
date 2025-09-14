from aiogram_dialog import DialogManager


async def get_i18n(**kwargs):
    dm = kwargs.get('dialog_manager')
    i18n = dm.middleware_data.get('i18n', {})  
    return {'i18n': i18n}