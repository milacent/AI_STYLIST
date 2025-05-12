import re

def checker(password):
    """
    Функция для проверки пароля.
    Проверяет, что пароль содержит хотя бы одну заглавную букву,
    хотя бы одну цифру и имеет длину не менее 8 символов.
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True
