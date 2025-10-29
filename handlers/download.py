import logging
from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "download_app")
async def download_app_handler(call: types.CallbackQuery):
    """Обрабатывает нажатие на кнопку 'Скачать приложение'."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Iphone", callback_data="instructions_iphone")],
        [InlineKeyboardButton(text="📱 Android", callback_data="instructions_android")],
        [InlineKeyboardButton(text="📱 Huawei и HONOR", callback_data="instructions_huawei")],
        [InlineKeyboardButton(text="💻 MacOS", callback_data="instructions_macos")],
        [InlineKeyboardButton(text="🖥️ Windows", callback_data="instructions_windows")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_profile")],
    ])
    await call.message.edit_text(
        "На какое устройство желаете установить приложение?\n"
        "К одному ключу можно подключить до 3 устройств.",
        reply_markup=keyboard
    )
    await call.answer()


@router.callback_query(F.data == "instructions_iphone")
async def instructions_iphone_handler(call: types.CallbackQuery):
    text = (
        "<b>📱 Настройка для iPhone/iPad:</b>\n\n"
        "1. <b>Установите приложение</b>\n "  
        "<a href='https://apps.apple.com/app/id6476628951'>v2RayTun</a>\n"
        "<a href='https://apps.apple.com/us/app/happ-proxy-utility/id6504287215'>(Резервная ссылка на установку)</a>\n"
        "2. <b>Скопируйте</b> ссылку подписки (нажмите на неё), которую отправил бот\n"  
        "3. <b>Откройте</b> приложение и вставьте ссылку\n"  
        "4. <b>Подключитесь</b> к серверу"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data="download_app")]
    ])
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

@router.callback_query(F.data == "instructions_android")
async def instructions_android_handler(call: types.CallbackQuery):
    text = (
        "<b>📱 Настройка для Android:</b>\n\n"
        "1. <b>Установите приложение</b>\n "
        "<a href='https://play.google.com/store/apps/details?id=com.v2raytun\.android'>Скачать из Google Store</a> или установите APK\n"
        "<a href='https://github.com/Happ-proxy/happ-android/releases/latest/download/Happ.apk'>Скачать APK</a>\n"
        "2. <b>Скопируйте</b> ссылку подписки (нажмите на неё), которую отправил бот\n"
        "3. <b>Откройте</b> приложение и вставьте ссылку\n"
        "4. <b>Подключитесь</b> к серверу"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data="download_app")]
    ])
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

@router.callback_query(F.data == "instructions_huawei")
async def instructions_huawei_handler(call: types.CallbackQuery):
    text = (
        "<b>📱 Настройка для Huawei и HONOR:</b>\n\n"
        "Инструкция для Huawei, Honor и других Android устройств без Google Play с APK файлом по ссылке ниже:\n"
        "<a href='https://t.me/v2raytunhuawei'>Открыть инструкцию</a>\n"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data="download_app")]
    ])
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

@router.callback_query(F.data == "instructions_macos")
async def instructions_macos_handler(call: types.CallbackQuery):
    text = (
        "<b>💻 Настройка для MacOS:</b>\n\n"
        "1. <b>Установите приложение</b>\n "
        "<a href='https://apps.apple.com/app/id6476628951'>Cкачать из App Store</a>\n"
        "2. <b>Скопируйте</b> ссылку подписки (нажмите на неё), которую отправил бот\n"
        "3. <b>Откройте</b> приложение и вставьте ссылку\n"
        "4. <b>Подключитесь</b> к серверу"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data="download_app")]
    ])
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

@router.callback_query(F.data == "instructions_windows")
async def instructions_windows_handler(call: types.CallbackQuery):
    text = (
        "<b>💻 Настройка для Windows:</b>\n\n"
        "1. <b>Установите приложение</b>\n "
        "<a href='https://storage.v2raytun.com/v2RayTun_Setup.exe'>Скачать v2RayTun</a>\n"
        "2. <b>Скопируйте</b> ссылку подписки (нажмите на неё), которую отправил бот\n"
        "3. <b>Откройте</b> приложение и вставьте ссылку\n"
        "4. <b>Подключитесь</b> к серверу"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data="download_app")]
    ])
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

