from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import requests
from django.utils import timezone
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
from collections import Counter

class Info(models.Model):
    """
       Дополнительная информация о пользователе профиля.

       Attributes:
           user (User): Связь один-ко-многим с моделью User
           gender (int): Пол пользователя (1 - мужской, 2 - женский)
           about_me (str): Краткая биография или описание пользователя (макс. 300 символов)
       """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gender = models.IntegerField()
    about_me = models.CharField(max_length=300)

class Post(models.Model):
    """
        Модель пользовательского поста с возможностью добавления изображения.

        Attributes:
            user (User): Автор поста
            title (str): Заголовок поста (макс. 50 символов)
            image (ImageField): Опциональное изображение для поста
            description (str): Основной текст поста (макс. 5000 символов)
        """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    description = models.CharField(max_length=5000)

class Comment(models.Model):
    """
        Комментарии к постам пользователей.

        Attributes:
            user (User): Автор комментария
            content (str): Текст комментария (макс. 500 символов)
            post (Post): Связанный пост, к которому оставлен комментарий
        """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class LikePost(models.Model):
    """
        Система лайков для постов.

        Attributes:
            user (User): Пользователь, поставивший лайк
            post (Post): Пост, который был лайкнут
        """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class LikeComment(models.Model):
    """
        Система лайков для комментариев.

        Attributes:
            user (User): Пользователь, поставивший лайк
            comment (Comment): Комментарий, который был лайкнут
        """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

class Item(models.Model):
    """
        Пользовательские предметы/ссылки для системы рекомендаций.

        Attributes:
            user (User): Владелец предмета
            url (URLField): Ссылка на внешний ресурс с описанием предмета
            image (ImageField): Визуальное представление предмета
        """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    image = models.ImageField()

class UserGrade(models.Model):
    """
       Система оценки пользователей и предметов.

       Attributes:
           user (User): Пользователь, выставляющий оценку
           info (Info): Связанная информация профиля
           item (Item): Оцениваемый предмет
           grade (int): Значение оценки от 1 до 5
       """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    info = models.ForeignKey(Info, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    grade = models.IntegerField()

class ClothingItem(models.Model):
    """
        База данных элементов одежды с характеристиками для рекомендательной системы.

        Attributes:
            category (str): Категория одежды из предопределенного списка
            name (str): Название элемента одежды
            image_name (str): Название файла изображения элемента
            min_temp (int): Минимальная рекомендованная температура ношения
            max_temp (int): Максимальная рекомендованная температура ношения
            color (str): Основной цвет элемента
            style (str): Стилевая принадлежность из предопределенных вариантов
            material (str): Материал изготовления из предопределенных вариантов
            vector (str): Сериализованный вектор для расчетов схожести

        Choices:
            categories: Варианты категорий одежды
            Styles: Доступные стилевые направления
            Material: Типы материалов изготовления
        """
    categories = [
        ('hats', 'Головные уборы'),
        ('outerwear', 'Верхняя одежда'),
        ('tops', 'Топы'),
        ('bottoms', 'Низы'),
        ('shoes', 'Обувь')
    ]

    class Styles(models.TextChoices):
        """Доступные стилевые направления элементов одежды."""
        classic = "classic", "classic"
        casual = "casual", "casual"
        sport = "sport", "sport"
        business = "business", "business"
        streetwear = "streetwear", "streetwear"
        retro = "retro", "retro"
        punk = "punk", "punk"
        military = "military", "military"
        grunge = "grunge", "grunge"
        minimalism = "minimalism", "minimalism"

    class Material(models.TextChoices):
        """Типы материалов для элементов одежды."""
        cotton = "cotton", "cotton"
        polyester = "polyester", "polyester"
        wool = "wool", "wool"
        leather = "leather", "leather"
        denim = "denim", "denim"
        flax = "flax", "flax"
        suede = "suede", "suede"

    category = models.CharField(max_length=10, choices=categories)
    name = models.CharField(max_length=100)
    image_name = models.CharField(max_length=100)
    min_temp = models.IntegerField(default=0)
    max_temp = models.IntegerField(default=0)
    color = models.CharField(max_length=15)
    style = models.TextField(choices=Styles.choices, default="classic")
    material = models.CharField(choices=Material.choices, max_length=20, default="cotton")
    vector = models.TextField(null=True, blank=True)

    def get_vector(self):
        """
                Преобразует сериализованный вектор в numpy array.

                Returns:
                    np.ndarray or None: Векторное представление элемента одежды
                """
        try:
            return np.array(json.loads(self.vector))
        except Exception:
            return None

class Looks(models.Model):
    """
        Полные комплекты одежды с метаданными для рекомендаций.

        Содержит информацию о всех элементах комплекта:
        - Головные уборы
        - Верхняя одежда
        - Топы
        - Низы
        - Обувь

        Для каждого элемента хранятся:
        - Название
        - Изображение
        - Цвет
        - Материал
        - Стиль
        - Векторное представление

        Attributes:
            temp_range (str): Температурный диапазон для комплекта
            general_vector (str): Объединенное векторное представление комплекта
            saved_by (ManyToManyField): Пользователи, сохранившие комплект
        """
    temp_range = models.CharField(max_length=20, default='unknown_range')

    head = models.CharField(max_length=255, default='no_head')
    head_image = models.CharField(max_length=255, default='default.png')
    head_color = models.CharField(max_length=100, default='unknown')
    head_material = models.CharField(max_length=100, default='unknown')
    head_style = models.CharField(max_length=100, default='unknown')
    head_vector = models.CharField(max_length=255, default='no_vector')

    outerwear = models.CharField(max_length=255, default='no_outerwear')
    outerwear_image = models.CharField(max_length=255, default='default.png')
    outerwear_color = models.CharField(max_length=100, default='unknown')
    outerwear_material = models.CharField(max_length=100, default='unknown')
    outerwear_style = models.CharField(max_length=100, default='unknown')
    outerwear_vector = models.CharField(max_length=255, default='no_vector')

    top = models.CharField(max_length=255, default='no_top')
    top_image = models.CharField(max_length=255, default='default.png')
    top_color = models.CharField(max_length=100, default='unknown')
    top_material = models.CharField(max_length=100, default='unknown')
    top_style = models.CharField(max_length=100, default='unknown')
    top_vector = models.CharField(max_length=255, default='no_vector')

    bottom = models.CharField(max_length=255, default='no_bottom')
    bottom_image = models.CharField(max_length=255, default='default.png')
    bottom_color = models.CharField(max_length=100, default='unknown')
    bottom_material = models.CharField(max_length=100, default='unknown')
    bottom_style = models.CharField(max_length=100, default='unknown')
    bottom_vector = models.CharField(max_length=255, default='no_vector')

    shoes = models.CharField(max_length=255, default='no_shoes')
    shoes_image = models.CharField(max_length=255, default='default.png')
    shoes_color = models.CharField(max_length=100, default='unknown')
    shoes_material = models.CharField(max_length=100, default='unknown')
    shoes_style = models.CharField(max_length=100, default='unknown')
    shoes_vector = models.CharField(max_length=255, default='no_vector')

    general_vector = models.CharField(max_length=1024, default='no_general_vector')
    saved_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='saved_looks', blank=True)

    def get_vector(self):
        """
                Декодирует общий вектор комплекта из строки в numpy array.

                Returns:
                    np.ndarray or None: Векторное представление комплекта
                """
        try:
            return np.array(json.loads(self.general_vector))
        except Exception:
            return None

    @classmethod
    def get_recommendations(cls, user, top_n=5):
        """
                Генерирует персонализированные рекомендации комплектов на основе предпочтений.

                Args:
                    user (User): Целевой пользователь
                    top_n (int): Количество возвращаемых рекомендаций

                Returns:
                    list[Looks]: Список рекомендованных комплектов
                """
        liked_looks = LikedLook.objects.filter(user=user)
        liked_vectors = []

        for liked in liked_looks:
            vec = liked.look.get_vector()
            if vec is not None:
                liked_vectors.append(vec)

        if not liked_vectors:
            return cls.objects.exclude(
                id__in=DislikedLook.objects.filter(user=user).values_list('look_id', flat=True)).order_by('?')[:top_n]

        user_pref_vector = np.mean(liked_vectors, axis=0).reshape(1, -1)

        candidates = cls.objects.exclude(id__in=liked_looks.values_list('look_id', flat=True)).exclude(
            id__in=DislikedLook.objects.filter(user=user).values_list('look_id', flat=True))

        scored = []
        for look in candidates:
            vec = look.get_vector()
            if vec is not None:
                sim = cosine_similarity(user_pref_vector, vec.reshape(1, -1))[0][0]
                if sim > 0.6:
                    scored.append((sim, look))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [look for _, look in scored[:top_n]]

    @classmethod
    def generate_from_preferences(cls, user):
        """
                Генерирует новый комплект на основе предпочтений пользователя.

                Args:
                    user (User): Целевой пользователь

                Returns:
                    Looks or None: Сгенерированный комплект или None при ошибке
                """
        liked_looks = LikedLook.objects.filter(user=user).select_related('look')
        if not liked_looks.exists():
            return None

        styles = []
        materials = []

        for like in liked_looks:
            look = like.look
            styles += [look.top_style, look.bottom_style, look.outerwear_style, look.shoes_style]
            materials += [look.top_material, look.bottom_material, look.outerwear_material, look.shoes_material]

        top_style = Counter(styles).most_common(1)[0][0]
        top_material = Counter(materials).most_common(1)[0][0]

        top = ClothingItem.objects.filter(category='tops', style=top_style, material=top_material).order_by('?').first()
        bottom = ClothingItem.objects.filter(category='bottoms', style=top_style, material=top_material).order_by('?').first()
        shoes = ClothingItem.objects.filter(category='shoes', style=top_style, material=top_material).order_by('?').first()

        if not (top and bottom and shoes):
            return None

        items = [top, bottom, shoes]
        vectors = [item.get_vector() for item in items if item.get_vector() is not None]
        if not vectors:
            return None
        general_vector = json.dumps(np.mean(vectors, axis=0).tolist())

        return cls.objects.create(
            top=top.name,
            top_image=top.image_name,
            top_color=top.color,
            top_style=top.style,
            top_material=top.material,

            bottom=bottom.name,
            bottom_image=bottom.image_name,
            bottom_color=bottom.color,
            bottom_style=bottom.style,
            bottom_material=bottom.material,

            shoes=shoes.name,
            shoes_image=shoes.image_name,
            shoes_color=shoes.color,
            shoes_style=shoes.style,
            shoes_material=shoes.material,

            general_vector=general_vector
        )

    @classmethod
    def get_for_temperature(cls, temp):
        """
                Подбирает подходящий комплект для указанной температуры.

                Args:
                    temp (int): Текущая температура в градусах Цельсия

                Returns:
                    Looks or None: Подходящий комплект или None если не найден
                """
        temp_ranges = {
            (-20, -10): "-20_-10",
            (-10, 0): "-10_0",
            (0, 10): "0_10",
            (10, 20): "10_20",
            (20, 30): "20_30"
        }

        for (min_t, max_t), range_str in temp_ranges.items():
            if min_t <= temp <= max_t:
                return cls.objects.filter(temp_range=range_str).order_by('?').first()
        return None

def get_current_weather(city='Moscow'):
    """
        Получает текущую температуру для указанного города через OpenWeatherMap API.

        Args:
            city (str): Название города на английском языке

        Returns:
            float or None: Температура в градусах Цельсия или None при ошибке
        """
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data['main']['temp']
    except Exception:
        return None

class LikedLook(models.Model):
    """
        История лайков пользователей для системы рекомендаций.

        Attributes:
            user (User): Пользователь, которому понравился комплект
            look (Looks): Понравившийся комплект
            created_at (datetime): Дата и время лайка
        """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    look = models.ForeignKey(Looks, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'look')

class DislikedLook(models.Model):
    """
       История дизлайков пользователей для улучшения рекомендаций.

       Attributes:
           user (User): Пользователь, отклонивший комплект
           look (Looks): Отклоненный комплект
           created_at (datetime): Дата и время дизлайка
       """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    look = models.ForeignKey(Looks, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'look')
