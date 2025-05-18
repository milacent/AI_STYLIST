from django.db import models
from django.contrib.auth.models import User


class Info(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #height = models.IntegerField()
    #weight = models.IntegerField()
    #chest = models.CharField(max_length=100, default='default_value')
    #waist = models.IntegerField()
    #hips = models.IntegerField()
    gender = models.IntegerField()
    about_me = models.CharField(max_length=300)

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    description = models.CharField(max_length=5000, default='')

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
    items = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    weather_grade = models.IntegerField()  # Насколько подходит по погоде -10 - зима +10 - жара
    description = models.CharField(max_length=2058, default='')
    style = models.CharField(max_length=100, choices=ClothingItem.Styles.choices, default="classic")