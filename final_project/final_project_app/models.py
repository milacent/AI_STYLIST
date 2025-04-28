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

    def get_temperature_folder(self):
        return f"{self.min_temp}_{self.max_temp}"


class Looks(models.Model):
    temp_range = models.CharField(max_length=20, default='unknown_range')

    # Head
    head = models.CharField(max_length=255, default='no_head')
    head_image = models.CharField(max_length=255, default='default.png')
    head_color = models.CharField(max_length=100, default='unknown')
    head_material = models.CharField(max_length=100, default='unknown')
    head_style = models.CharField(max_length=100, default='unknown')
    head_vector = models.CharField(max_length=255, default='no_vector')

    # Outerwear
    outerwear = models.CharField(max_length=255, default='no_outerwear')
    outerwear_image = models.CharField(max_length=255, default='default.png')
    outerwear_color = models.CharField(max_length=100, default='unknown')
    outerwear_material = models.CharField(max_length=100, default='unknown')
    outerwear_style = models.CharField(max_length=100, default='unknown')
    outerwear_vector = models.CharField(max_length=255, default='no_vector')

    # Top
    top = models.CharField(max_length=255, default='no_top')
    top_image = models.CharField(max_length=255, default='default.png')
    top_color = models.CharField(max_length=100, default='unknown')
    top_material = models.CharField(max_length=100, default='unknown')
    top_style = models.CharField(max_length=100, default='unknown')
    top_vector = models.CharField(max_length=255, default='no_vector')

    # Bottom
    bottom = models.CharField(max_length=255, default='no_bottom')
    bottom_image = models.CharField(max_length=255, default='default.png')
    bottom_color = models.CharField(max_length=100, default='unknown')
    bottom_material = models.CharField(max_length=100, default='unknown')
    bottom_style = models.CharField(max_length=100, default='unknown')
    bottom_vector = models.CharField(max_length=255, default='no_vector')

    # Shoes
    shoes = models.CharField(max_length=255, default='no_shoes')
    shoes_image = models.CharField(max_length=255, default='default.png')
    shoes_color = models.CharField(max_length=100, default='unknown')
    shoes_material = models.CharField(max_length=100, default='unknown')
    shoes_style = models.CharField(max_length=100, default='unknown')
    shoes_vector = models.CharField(max_length=255, default='no_vector')

    # General
    general_vector = models.CharField(max_length=1024, default='no_general_vector')
    saved_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='saved_looks',
        blank=True
    )

    def __str__(self):
        return f"Look for {self.temp_range}"

    @classmethod
    def get_for_temperature(cls, temp):
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
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data['main']['temp']
    except Exception as e:
        return None


class LikedLook(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    look = models.ForeignKey(Looks, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'look')


class DislikedLook(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    look = models.ForeignKey(Looks, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'look')

