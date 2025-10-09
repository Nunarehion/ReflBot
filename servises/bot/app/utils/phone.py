import re

def validate_phone_number(phone: str) -> bool:
    """Валидация номера телефона."""
    clean_phone = re.sub(r'[^\d+]', '', phone)
    patterns = [
        r'^\+7\d{10}$',  # +7XXXXXXXXXX
        r'^8\d{10}$',    # 8XXXXXXXXXX
        r'^7\d{10}$'     # 7XXXXXXXXXX
    ]
    return any(re.match(pattern, clean_phone) for pattern in patterns)

def normalize_phone_number(phone: str) -> str:
    """Нормализует номер телефона к формату +7XXXXXXXXXX."""
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    if clean_phone.startswith('+7'):
        return clean_phone
    elif clean_phone.startswith('8'):
        return '+7' + clean_phone[1:]
    elif clean_phone.startswith('7'):
        return '+' + clean_phone
    else:
        return '+7' + clean_phone

