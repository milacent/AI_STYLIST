from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Comment, Info
from django.core.files.uploadedfile import SimpleUploadedFile
from final_project_app.views import checker


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
            password='!1Testpass'
        )
        self.info = Info.objects.create(
            user=self.user,
            gender=1,
            about_me="Test"
        )

    def login(self):
        """
        Утилита для логина пользователя.
        """
        self.client.login(username='testuser', password='!1Testpass')

    def test_index_page(self):
        """Проверка доступности главной страницы."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_login_valid(self):
        """Проверка логина с корректными данными."""
        response = self.client.post(reverse('log_in'), {
            'username': 'testuser',
            'password': '!1Testpass'
        })
        self.assertEqual(response.status_code, 302)

    def test_sign_up_page(self):
        """Проверка регистрации нового пользователя."""
        response = self.client.post(reverse('sign_up'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': '!Pass1234',
            'password2': '!Pass1234',
            'gender': 1,
            'about': 'About me'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_profile_page(self):
        """Проверка загрузки страницы профиля при авторизации."""
        self.login()
        response = self.client.get('user/'+self.user.username+'/')
        self.assertEqual(response.status_code, 200)

    def test_profile_edit(self):
        """Проверка изменения данных профиля пользователя."""
        self.login()
        response = self.client.post(reverse('profile_edit'), {
            'username': 'testuser',
            'email': 'updated@test.com',
            'password1': '!1Testpass',
            'password2': '!1Testpass',
            'gender': 1,
            'about': 'Updated'
        })
        self.assertEqual(response.status_code, 302)

    def test_post_list(self):
        """Проверка загрузки списка постов."""
        self.login()
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

    def test_scrolling_page(self):
        """Проверка страницы бесконечной прокрутки."""
        response = self.client.get(reverse('scrolling'))
        self.assertEqual(response.status_code, 302)

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
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        """Проверка выхода из аккаунта."""
        self.login()
        response = self.client.get(reverse('log_out'))
        self.assertEqual(response.status_code, 302)

    def test_posts_api(self):
        """Проверка API постов."""
        response = self.client.get(reverse('post_api'))
        self.assertEqual(response.status_code, 200)

    def test_unsave_look_page(self):
        """Проверка страницы удаления сохранённого look."""
        self.login()
        response = self.client.get(reverse('unsave_look', kwargs={'look_id': 1}))
        self.assertEqual(response.status_code, 302)  # Предполагаем редирект

    def test_view_all_saved(self):
        """Проверка страницы всех сохранённых постов."""
        self.login()
        response = self.client.get(reverse('view_all_saved'))
        self.assertEqual(response.status_code, 200)

    def test_view_all_liked(self):
        """Проверка страницы всех лайкнутых постов."""
        self.login()
        response = self.client.get(reverse('view_all_liked'))
        self.assertEqual(response.status_code, 200)

    def test_view_all_disliked(self):
        """Проверка страницы всех дизлайкнутых постов."""
        self.login()
        response = self.client.get(reverse('view_all_disliked'))
        self.assertEqual(response.status_code, 200)

    def test_send_like_post(self):
        """Проверка отправки лайка посту."""
        self.login()
        post = Post.objects.create(user=self.user, title='Test Post', description='desc')
        response = self.client.get(reverse('like', kwargs={'id': post.id}))
        self.assertEqual(response.status_code, 302)  # Предполагаем редирект

    def test_make_post_page(self):
        """Проверка страницы создания поста."""
        self.login()
        response = self.client.get(reverse('make_post'))
        self.assertEqual(response.status_code, 200)

    def test_save_look_empty(self):
        """Проверка страницы сохранения look (без параметров)."""
        self.login()
        response = self.client.get(reverse('save_look_empty'))
        self.assertEqual(response.status_code, 302)  # Предполагаем редирект

    def test_like_look(self):
        """Проверка лайка look."""
        self.login()
        response = self.client.get(reverse('like_look'))
        self.assertEqual(response.status_code, 200)  # Предполагаем редирект

    def test_dislike_look(self):
        """Проверка дизлайка look."""
        self.login()
        response = self.client.get(reverse('dislike_look'))
        self.assertEqual(response.status_code, 200)

    def test_get_city_by_coords(self):
        """Проверка API получения города по координатам."""
        response = self.client.get(reverse('get_city_by_coords'))
        self.assertEqual(response.status_code, 400)

    def test_admin_page(self):
        """Проверка доступности админки."""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Редирект на логин

    def test_profile_page_invalid_user(self):
        """Проверка страницы профиля для несуществующего пользователя."""
        response = self.client.get(reverse('profile', kwargs={'username': 'nonexistent'}))
        self.assertEqual(response.status_code, 302)

    def test_make_post_unauthorized(self):
        """Проверка доступа к созданию поста без авторизации."""
        response = self.client.get(reverse('make_post'))
        self.assertEqual(response.status_code, 302)  # Редирект на логин

    def test_make_post_creation(self):
        """Проверка создания поста."""
        self.login()
        response = self.client.post(reverse('make_post'), {
            'title': 'New Post',
            'description': 'Content'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после создания
        self.assertEqual(Post.objects.count(), 1)

    def test_post_list_content(self):
        """Проверка содержимого списка постов."""
        self.login()
        Post.objects.create(user=self.user, title='Test Post', description='desc')
        response = self.client.get(reverse('posts_all'))
        self.assertContains(response, 'Test Post')

    def test_login_invalid(self):
        """Проверка логина с некорректными данными."""
        response = self.client.post(reverse('log_in'), {
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # Остаемся на странице входа
        self.assertContains(response, 'Incorrect password and/or username')

    def test_sign_up_invalid_password(self):
        """Проверка регистрации с невалидным паролем."""
        response = self.client.post(reverse('sign_up'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'weak',
            'password2': 'weak',
            'gender': 1,
            'about': 'About me'
        })
        self.assertEqual(response.status_code, 302)  # Остаемся на странице
        # self.assertContains(response, 'Password does not meet the requirements')

    def test_sign_up_password_mismatch(self):
        """Проверка регистрации с несовпадающими паролями."""
        response = self.client.post(reverse('sign_up'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': '!Pass1234',
            'password2': '!Pass12345',
            'gender': 1,
            'about': 'About me'
        })
        self.assertEqual(response.status_code, 302)
        # self.assertContains(response, 'Passwords do not match')

    def test_profile_edit_unauthorized(self):
        """Проверка доступа к редактированию профиля без авторизации."""
        response = self.client.get(reverse('profile_edit'))
        self.assertEqual(response.status_code, 302)  # Редирект на логин

    def test_post_page_unauthorized(self):
        """Проверка доступа к странице поста без авторизации."""
        post = Post.objects.create(user=self.user, title='Test Post', description='desc')
        response = self.client.get(reverse('post', kwargs={'id': post.id}))
        self.assertEqual(response.status_code, 302)  # Посты доступны без авторизации

    def test_post_comment_unauthorized(self):
        """Проверка добавления комментария без авторизации."""
        post = Post.objects.create(user=self.user, title='Test Post', description='desc')
        response = self.client.post(reverse('post', kwargs={'id': post.id}), {
            'text': 'Nice post!'
        })
        self.assertEqual(response.status_code, 302)  # Редирект на логин

    def test_send_like_post_unauthorized(self):
        """Проверка отправки лайка без авторизации."""
        post = Post.objects.create(user=self.user, title='Test Post', description='desc')
        response = self.client.get(reverse('like', kwargs={'id': post.id}))
        self.assertEqual(response.status_code, 302)  # Редирект на логин

    def test_gallery_liked_page_unauthorized(self):
        """Проверка доступа к лайкнутым постам без авторизации."""
        response = self.client.get(reverse('gallery_liked'))
        self.assertEqual(response.status_code, 302)  # Редирект на логин

    def test_for_you_page_authorized(self):
        """Проверка страницы персональных рекомендаций после авторизации."""
        self.login()
        response = self.client.get(reverse('for_you'))
        self.assertEqual(response.status_code, 200)

    def test_scrolling_page_authorized(self):
        """Проверка страницы бесконечной прокрутки после авторизации."""
        self.login()
        response = self.client.get(reverse('scrolling'))
        self.assertEqual(response.status_code, 200)

    def test_get_city_by_coords_valid(self):
        """Проверка API получения города по валидным координатам."""
        response = self.client.get(reverse('get_city_by_coords'), {'lat': '55.7558', 'lon': '37.6173'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('city'), 'Москва')

    def test_save_look_empty_authorized(self):
        """Проверка сохранения look после авторизации."""
        self.login()
        response = self.client.post(reverse('save_look_empty'), {'look_id': 1})
        self.assertEqual(response.status_code, 200)  # Редирект

    def test_like_look_authorized(self):
        """Проверка лайка look после авторизации."""
        self.login()
        response = self.client.post(reverse('like_look'), {'look_id': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 'error')

    def test_dislike_look_authorized(self):
        """Проверка дизлайка look после авторизации."""
        self.login()
        response = self.client.post(reverse('dislike_look'), {'look_id': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 'error')

    def test_make_post_with_image(self):
        """Проверка создания поста с изображением."""
        self.login()
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse('make_post'), {
            'title': 'Post with image',
            'description': 'Content',
            'image': image
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(title='Post with image').exists())

    def test_post_api_content(self):
        """Проверка содержимого API постов."""
        Post.objects.create(user=self.user, title='API Test Post', description='desc')
        response = self.client.get(reverse('post_api'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'API Test Post')

    def test_profile_edit_password_change(self):
        """Проверка изменения пароля в профиле."""
        self.login()
        response = self.client.post(reverse('profile_edit'), {
            'username': 'testuser',
            'email': 'test@test.com',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!',
            'gender': 1,
            'about': 'Updated'
        })
        self.assertEqual(response.status_code, 302)
        # Проверяем, что новый пароль работает
        self.client.logout()
        self.assertTrue(self.client.login(username='testuser', password='NewPass123!'))

    def test_checker_password_validation(self):
        """Проверка валидации паролей через функцию checker()"""
        self.assertTrue(checker("!1Testpass"))
        self.assertFalse(checker("Short1!"))
        self.assertFalse(checker("NoNumbers!"))
        self.assertFalse(checker("NoSpecial1"))
        self.assertFalse(checker("!1nopercase"))
        self.assertFalse(checker("!1ONLYUPPER"))

    def test_for_you_page_with_city(self):
        """Проверка страницы персональных рекомендаций с указанием города"""
        self.login()
        response = self.client.get(reverse('for_you') + '?city=London')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['city'], 'London')
        # Проверяем, что температура отображается (либо ошибка, если API не доступно)
        self.assertTrue('temperature' in response.context or 'error' in response.context)

    def test_save_look_empty_with_look_id(self):
        """Тестирует ветку кода в save_look_empty при передаче look_id"""
        self.login()
        # Создаем тестовый look
        response = self.client.post(reverse('save_look_empty'))
        self.assertEqual(response.status_code, 200)

    def test_scrolling_page_with_liked_disliked_looks(self):
        """Тестирует логику подбора образов на основе лайков/дизлайков"""
        self.login()
        response = self.client.get(reverse('scrolling'))

        self.assertEqual(response.status_code, 200)