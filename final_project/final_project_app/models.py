from cgi import maxlen

from django.db import models
from django.contrib.auth.models import User


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
    #

class Looks(models.Model):
    items = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    weather_grade = models.IntegerField() # Насколько подходит по погоде -10 - зима +10 - жара
    description = models.CharField(max_length=2058)

class UserGrade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    info = models.ForeignKey(Info, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    grade = models.IntegerField()
# Create your models here.
