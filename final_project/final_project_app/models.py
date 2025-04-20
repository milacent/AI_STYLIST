from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import requests
from django.utils import timezone

class Info(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    height = models.IntegerField()
    weight = models.IntegerField()
    chest = models.IntegerField()
    waist = models.IntegerField()
    hips = models.IntegerField()
    gender = models.IntegerField()
    about_me = models.CharField(max_length=300)

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    description = models.CharField(max_length=5000)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class LikePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class LikeComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    image = models.ImageField()
    # color
    # material
    # style
    # whether_grade

class UserGrade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    info = models.ForeignKey(Info, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    grade = models.IntegerField()


class ClothingItem(models.Model):
    categories= [
        ('hats', 'Головные уборы'),
        ('outerwear', 'Верхняя одежда'),
        ('tops', 'Топы'),
        ('bottoms', 'Низы'),
        ('shoes', 'Обувь')
    ]

    class Styles(models.TextChoices):
        classic = "classic", ("classic")
        casual = "casual", ("casual")
        sport = "sport", ("sport")
        business = "business", ("business")
        streetwear = "streetwear", ("streetwear")
        retro = "retro", ("retro")
        punk = "punk", ("punk")
        military = "military", ("military")
        grunge = "grunge", ("grunge")
        minimalism = "minimalism", ("minimalism")

    class Material(models.TextChoices):
        cotton = "cotton", ("cotton")
        polyester = "polyester", ("polyester")
        wool = "wool", ("wool")
        leather = "leather", ("leather")
        denim = "denim", ("denim")
        flax = "flax", ("flax")
        suede = "suede", ("suede")


    category = models.CharField(max_length=10, choices=categories)
    name = models.CharField(max_length=100)
    image_name = models.CharField(max_length=100)
    min_temp = models.IntegerField(default=0)
    max_temp = models.IntegerField(default=0)
    color = models.CharField(max_length=15)
    style = models.TextField(choices=Styles.choices, default="classic")
    material = models.CharField(choices=Material.choices, max_length=20, default="cotton")


class Looks(models.Model):
    # items = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    weather_grade = models.IntegerField()  # Насколько подходит по погоде -10 - зима +10 - жара
    description = models.CharField(max_length=2058)
    style = models.CharField(choices=ClothingItem.Styles.choices, default="classic")

    head = models.ForeignKey(ClothingItem, related_name='head_looks', null=True, blank=True, on_delete=models.SET_NULL)
    outerwear = models.ForeignKey(ClothingItem, related_name='outerwear_looks', null=True, blank=True,
                                  on_delete=models.SET_NULL)
    top = models.ForeignKey(ClothingItem, related_name='top_looks', null=True, blank=True, on_delete=models.SET_NULL)
    bottom = models.ForeignKey(ClothingItem, related_name='bottom_looks', null=True, blank=True,
                               on_delete=models.SET_NULL)
    shoes = models.ForeignKey(ClothingItem, related_name='shoes_looks', null=True, blank=True,
                              on_delete=models.SET_NULL)

    min_temp = models.IntegerField(default=0)
    max_temp = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Look for {self.get_temperature_range()} ({self.style})"

    def get_temperature_range(self):
        return f"{self.min_temp}°C to {self.max_temp}°C"

    @classmethod
    def get_temperature_folder(cls, temp):
        """Возвращает строку для папки с изображениями по температуре"""
        if temp <= -10:
            return "-20_-10"
        elif temp <= 0:
            return "-10_0"
        elif temp <= 10:
            return "0_10"
        elif temp <= 20:
            return "10_20"
        else:
            return "20_30"

        # Подбираем вещи
        categories = {
            'head': 'head',
            'top': 'tops',
            'bottom': 'bottoms',
            'shoes': 'shoes'
        }

        items = {
            field: ClothingItem.objects.filter(
                category=category,
                min_temp__lte=max_t,
                max_temp__gte=min_t
            ).order_by('?').first()
            for field, category in categories.items()
        }

        if max_t < 20:
            items['outerwear'] = ClothingItem.objects.filter(
                category='outerwear',
                min_temp__lte=max_t,
                max_temp__gte=min_t
            ).order_by('?').first()

        return cls.objects.create(
            min_temp=min_t,
            max_temp=max_t,
            weather_grade=temp,
            description="Автоматически сгенерированный образ",
            **items
        )

    @classmethod
    def get_current_weather(cls, city='Moscow'):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.WEATHER_API_KEY}&units=metric"
            response = requests.get(url, timeout=5)
            data = response.json()
            return data['main']['temp']
        except:
            return 0

    @classmethod
    def generate_for_city(cls, city='Moscow'):
        """Генерация образа для указанного города"""
        temp = cls.get_current_weather(city)
        return cls.generate_for_temperature(temp)

