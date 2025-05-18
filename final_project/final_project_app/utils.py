import re
import requests
from django.conf import settings


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

def get_weather_conditions(city='Moscow'):
    """
    Получает погодные условия для любого города.
    Возвращает строку: 'ясно', 'облачно', 'дождь', 'снег' или 'не определено'.
    """
    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={settings.WEATHER_API_KEY}&units=metric"
    )
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        weather_status = data.get('weather', [{}])[0].get('main', '').lower()

        mapping = {
            'rain': 'дождь',
            'drizzle': 'дождь',
            'thunderstorm': 'дождь',
            'snow': 'снег',
            'clear': 'ясно',
            'clouds': 'облачно',
        }
        return mapping.get(weather_status, 'не определено')
    except Exception:
        return None
