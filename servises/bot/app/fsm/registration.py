from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    """Состояния для процесса регистрации."""
    waiting_for_phone = State()
    waiting_for_referral_code = State()