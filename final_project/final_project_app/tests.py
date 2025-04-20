from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Info, Post, Comment, LikePost
from django.core.files.uploadedfile import SimpleUploadedFile


class ProjectTests(TestCase):
    """
    Набор тестов для проверки основных пользовательских функций веб-приложения:
    аутентификация, работа с постами, профилем, лайками и навигационными страницами.
    """

    def setUp(self):
        """
        Подготовка тестовых данных: создание пользователя и информации о нём.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass'
        )
        self.info = Info.objects.create(
            user=self.user,
            height=170,
            weight=65,
            chest=90,
            waist=70,
            hips=95,
            gender=1,
            about_me="Test"
        )

    def login(self):
        """
        Утилита для логина пользователя.
        """
        self.client.login(username='testuser', password='testpass')

    def test_index_page(self):
        """Проверка доступности главной страницы."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_login_valid(self):
        """Проверка логина с корректными данными."""
        response = self.client.post(reverse('log_in'), {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 302)

    def test_sign_up_page(self):
        """Проверка регистрации нового пользователя."""
        response = self.client.post(reverse('sign_up'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'pass1234',
            'password2': 'pass1234',
            'height': 170,
            'weight': 60,
            'chest': 90,
            'waist': 70,
            'hips': 95,
            'gender': 1,
            'about': 'About me'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_profile_page(self):
        """Проверка загрузки страницы профиля при авторизации."""
        self.login()
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_profile_edit(self):
        """Проверка изменения данных профиля пользователя."""
        self.login()
        response = self.client.post(reverse('profile_edit'), {
            'username': 'testuser',
            'email': 'updated@test.com',
            'password1': 'testpass',
            'password2': 'testpass',
            'height': 180,
            'weight': 70,
            'chest': 95,
            'waist': 75,
            'hips': 100,
            'gender': 1,
            'about': 'Updated'
        })
        self.assertEqual(response.status_code, 302)

    def test_post_list(self):
        """Проверка загрузки списка постов."""
        response = self.client.get(reverse('posts_all'))
        self.assertEqual(response.status_code, 200)

    def test_post_page(self):
        """Проверка открытия конкретного поста."""
        self.login()
        post = Post.objects.create(user=self.user, title='Test Post', description='desc')
        response = self.client.get(reverse('post', kwargs={'id': post.id}))
        self.assertEqual(response.status_code, 200)

    def test_post_comment(self):
        """Проверка добавления комментария к посту."""
        self.login()
        post = Post.objects.create(user=self.user, title='Test Post', description='desc')
        response = self.client.post(reverse('post', kwargs={'id': post.id}), {
            'text': 'Nice post!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)

    def test_catalog_page(self):
        """Проверка загрузки каталога."""
        self.login()
        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)

    def test_gallery_liked_page(self):
        """Проверка загрузки страницы с лайкнутыми постами."""
        self.login()
        post = Post.objects.create(user=self.user, title='Test Post', description='desc')
        LikePost.objects.create(user=self.user, post=post)
        response = self.client.get(reverse('gallery_liked'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, post.title)

    def test_scrolling_page(self):
        """Проверка страницы бесконечной прокрутки."""
        response = self.client.get(reverse('scrolling'))
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        """Проверка загрузки страницы 'О нас'."""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_terms_page(self):
        """Проверка загрузки страницы 'Условия использования'."""
        response = self.client.get(reverse('terms'))
        self.assertEqual(response.status_code, 200)

    def test_for_you_page(self):
        """Проверка страницы персональных рекомендаций."""
        response = self.client.get(reverse('for_you'))
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        """Проверка выхода из аккаунта."""
        self.login()
        response = self.client.get(reverse('log_out'))
        self.assertEqual(response.status_code, 302)
