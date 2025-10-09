from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from app.database.service import DatabaseService
from app.utils.phone import validate_phone_number, normalize_phone_number
from app.fsm.registration import RegistrationStates
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(lambda c: c.data == "register")
async def start_registration(callback: types.CallbackQuery, state: FSMContext):
    """Начинает процесс регистрации."""
    await callback.answer()
    await state.set_state(RegistrationStates.waiting_for_phone)
    
    await callback.message.edit_text(
        "📱 Пожалуйста, введите ваш номер телефона для регистрации.\n\n"
        "Форматы: +7XXXXXXXXXX, 8XXXXXXXXXX, 7XXXXXXXXXX"
    )

@router.callback_query(lambda c: c.data == "skip")
async def skip_referral_code(callback: types.CallbackQuery, state: FSMContext, db_service: DatabaseService):
    """Пропускает ввод реферального кода."""
    current_state = await state.get_state()
    if current_state != RegistrationStates.waiting_for_referral_code:
        await callback.answer("❌ Команда доступна только во время регистрации.")
        return
    
    # Получаем данные из состояния
    data = await state.get_data()
    phone = data.get("phone")
    
    if not phone:
        await callback.message.edit_text("❌ Ошибка: данные регистрации потеряны. Начните заново с /start")
        await state.clear()
        return
    
    # Создаём пользователя без реферального кода
    try:
        user = await db_service.add_user(
            telegram_id=callback.from_user.id,
            phone_number=phone,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name
        )
        
        await callback.message.edit_text(
            f"✅ Регистрация завершена!\n\n"
            f"👤 Ваш реферальный код: {user['referral_code']}\n"
            f"📊 Текущий баланс: {user['points']} баллов\n\n"
            f"⚠️ Для применения баллов аккаунт должен быть активирован администратором."
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Registration error for user {callback.from_user.id}: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при регистрации. Попробуйте позже или обратитесь к администратору."
        )
        await state.clear()

@router.message(lambda message: message.text and message.text.strip())
async def process_phone_input(message: types.Message, state: FSMContext, db_service: DatabaseService):
    """Обрабатывает ввод номера телефона."""
    current_state = await state.get_state()
    
    if current_state == RegistrationStates.waiting_for_phone:
        phone = message.text.strip()

        if not validate_phone_number(phone):
            await message.answer(
                "❌ Неверный формат номера телефона.\n"
                "Пожалуйста, введите номер в одном из форматов:\n"
                "• +7XXXXXXXXXX\n"
                "• 8XXXXXXXXXX\n"
                "• 7XXXXXXXXXX"
            )
            return
        
        normalized_phone = normalize_phone_number(phone)
        
        # Проверяем, не зарегистрирован ли уже этот номер
        existing_user = await db_service.get_user_by_phone(normalized_phone)
        if existing_user:
            await message.answer(
                "❌ Этот номер телефона уже зарегистрирован.\n"
                "Если это ваш номер, обратитесь к администратору."
            )
            return

        await state.update_data(phone=normalized_phone)
        
        # Переходим к вводу реферального кода
        await state.set_state(RegistrationStates.waiting_for_referral_code)
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip")]
        ])
        
        await message.answer(
            "✅ Номер телефона принят!\n\n"
            "🎁 Если у вас есть реферальный код, введите его сейчас, чтобы получить 100 баллов!\n"
            "⏰ У вас есть 48 часов после регистрации для ввода кода.\n\n"
            "Или нажмите кнопку ниже чтобы пропустить этот шаг.",
            reply_markup=keyboard
        )
    
    elif current_state == RegistrationStates.waiting_for_referral_code:
        referral_code = message.text.strip().upper()
        
        # Получаем данные из состояния
        data = await state.get_data()
        phone = data.get("phone")
        
        if not phone:
            await message.answer("❌ Ошибка: данные регистрации потеряны. Начните заново с /start")
            await state.clear()
            return
        
        # Создаём пользователя
        try:
            user = await db_service.add_user(
                telegram_id=message.from_user.id,
                phone_number=phone,
                username=message.from_user.username,
                full_name=message.from_user.full_name
            )
            
            logger.info(f"User {message.from_user.id} registered with phone {phone}")
            
            # Если введён реферальный код, обрабатываем его
            if referral_code and referral_code != "/SKIP":
                result = await db_service.process_referral_code(
                    new_user_telegram_id=message.from_user.id,
                    referral_code=referral_code
                )
                
                if result["success"]:
                    # Успешно применили реферальный код
                    await message.answer(
                        f"🎉 Регистрация завершена!\n\n"
                        f"✅ Реферальный код применён!\n"
                        f"💰 Вам начислено {result['new_user_points']} баллов\n"
                        f"👤 Ваш реферальный код: {user['referral_code']}\n"
                        f"📊 Текущий баланс: {user['points'] + result['new_user_points']} баллов\n\n"
                        f"⚠️ Для применения баллов аккаунт должен быть активирован администратором."
                    )
                    
                else:
                    # Ошибка с реферальным кодом
                    await message.answer(
                        f"❌ {result['error']}\n\n"
                        f"✅ Регистрация завершена без реферального кода\n"
                        f"👤 Ваш реферальный код: {user['referral_code']}\n"
                        f"📊 Текущий баланс: {user['points']} баллов\n\n"
                        f"⚠️ Для применения баллов аккаунт должен быть активирован администратором."
                    )
            else:
                # Регистрация без реферального кода
                await message.answer(
                    f"✅ Регистрация завершена!\n\n"
                    f"👤 Ваш реферальный код: {user['referral_code']}\n"
                    f"📊 Текущий баланс: {user['points']} баллов\n\n"
                    f"⚠️ Для применения баллов аккаунт должен быть активирован администратором."
                )
            
            # Очищаем состояние
            await state.clear()
            
        except Exception as e:
            logger.error(f"Registration error for user {message.from_user.id}: {e}")
            await message.answer(
                "❌ Произошла ошибка при регистрации. Попробуйте позже или обратитесь к администратору."
            )
            await state.clear()
