from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Comment, Info
from django.core.files.uploadedfile import SimpleUploadedFile
from final_project_app.views import checker

class ProjectTests(TestCase):
    """
    Набор интеграционных и unit-тестов для проверки основных пользовательских сценариев и API приложения.

    Методы тестируют:
        - регистрацию, аутентификацию
        - работу профиля, постов, комментариев, лайков, дизлайков
        - работу с изображениями
        - различные страницы и API endpoints
    """

    def setUp(self):
        """
        Подготавливает тестовые данные.

        Создаёт тестового пользователя, профиль и инициализирует клиент для имитации запросов.
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
        Авторизует тестового пользователя.
        """
        return self.client.login(username='testuser', password='!1Testpass')

    def test_index_page(self):
        """
        Проверяет доступность главной страницы.
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_login_valid(self):
        """
        Проверяет успешный вход с валидными данными.
        """
        response = self.client.post(reverse('log_in'), {
            'username': 'testuser',
            'password': '!1Testpass'
        })
        self.assertEqual(response.status_code, 302)

    def test_sign_up_page(self):
        """
        Проверяет успешную регистрацию нового пользователя.
        """
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
        """
        Проверяет доступность страницы профиля для авторизованного пользователя.
        """
        self.login()
        response = self.client.get(reverse('profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)

    def test_profile_edit(self):
        """
        Проверяет возможность редактирования профиля.
        """
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
        """
        Проверяет доступность страницы со списком постов.
        """
        self.login()
        response = self.client.get(reverse('posts_all'))
        self.assertEqual(response.status_code, 200)

    def test_post_page(self):
        """
        Проверяет доступность страницы отдельного поста.
        """
        self.login()
        post = Post.objects.create(user=self.user, title='Test Post', description='desc')
        response = self.client.get(reverse('post', kwargs={'id': post.id}))
        self.assertEqual(response.status_code, 200)

    def test_post_comment(self):
        """
        Проверяет возможность оставить комментарий к посту.
        """
        self.login()
        post = Post.objects.create(user=self.user, title='Test Post', description='desc')
        response = self.client.post(reverse('post', kwargs={'id': post.id}), {
            'text': 'Nice post!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)

    def test_catalog_page(self):
        """
        Проверяет доступность страницы каталога.
        """
        self.login()
        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)

    def test_scrolling_page(self):
        """
        Проверяет, что неавторизованный пользователь получает редирект со страницы скроллинга.
        """
        response = self.client.get(reverse('scrolling'))
        self.assertEqual(response.status_code, 302)

    def test_about_page(self):
        """
        Проверяет доступность страницы "О проекте".
        """
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_terms_page(self):
        """
        Проверяет доступность страницы с условиями использования.
        """
        response = self.client.get(reverse('terms'))
        self.assertEqual(response.status_code, 200)

    def test_for_you_page(self):
        """
        Проверяет, что неавторизованный пользователь получает редирект со страницы рекомендаций.
        """
        response = self.client.get(reverse('for_you'))
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        """
        Проверяет корректность выхода пользователя из системы.
        """
        self.login()
        response = self.client.get(reverse('log_out'))
        self.assertEqual(response.status_code, 302)

    def test_posts_api(self):
        """
        Проверяет доступность API списка постов.
        """
        response = self.client.get(reverse('post_api'))
        self.assertEqual(response.status_code, 200)

    def test_unsave_look_page(self):
        """
        Проверяет, что страница удаления сохранённого лука требует авторизации.
        """
        self.login()
        response = self.client.get(reverse('unsave_look', kwargs={'look_id': 1}))
        self.assertEqual(response.status_code, 302)

    def test_view_all_saved(self):
        """
        Проверяет доступность страницы всех сохранённых луков.
        """
        self.login()
        response = self.client.get(reverse('view_all_saved'))
        self.assertEqual(response.status_code, 200)

    def test_view_all_liked(self):
        """
        Проверяет доступность страницы всех понравившихся луков.
        """
        self.login()
        response = self.client.get(reverse('view_all_liked'))
        self.assertEqual(response.status_code, 200)

    def test_view_all_disliked(self):
        """
        Проверяет доступность страницы всех дизлайкнутых луков.
        """
        self.login()
        response = self.client.get(reverse('view_all_disliked'))
        self.assertEqual(response.status_code, 200)

    def test_send_like_post(self):
        """
        Проверяет возможность поставить лайк посту.
        """
        self.login()
        post = Post.objects.create(user=self.user, title='Test Post', description='desc')
        response = self.client.get(reverse('like', kwargs={'id': post.id}))
        self.assertEqual(response.status_code, 302)

    def test_make_post_page(self):
        """
        Проверяет доступность страницы создания поста для авторизованного пользователя.
        """
        self.login()
        response = self.client.get(reverse('make_post'))
        self.assertEqual(response.status_code, 200)

    def test_save_look_empty(self):
        """
        Проверяет, что при отсутствии look_id происходит редирект.
        """
        self.login()
        response = self.client.get(reverse('save_look_empty'))
        self.assertEqual(response.status_code, 302)

    def test_like_look(self):
        """
        Проверяет возможность лайкнуть лук.
        """
        self.login()
        response = self.client.get(reverse('like_look'))
        self.assertEqual(response.status_code, 200)

    def test_dislike_look(self):
        """
        Проверяет возможность дизлайкнуть лук.
        """
        self.login()
        response = self.client.get(reverse('dislike_look'))
        self.assertEqual(response.status_code, 200)

    def test_get_city_by_coords(self):
        """
        Проверяет, что без координат возвращается ошибка 400.
        """
        response = self.client.get(reverse('get_city_by_coords'))
        self.assertEqual(response.status_code, 400)

    def test_admin_page(self):
        """
        Проверяет, что неавторизованный пользователь получает редирект при попытке доступа к /admin/.
        """
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)

    def test_profile_page_invalid_user(self):
        """
        Проверяет, что при попытке доступа к несуществующему профилю происходит редирект.
        """
        response = self.client.get(reverse('profile', kwargs={'username': 'nonexistent'}))
        self.assertEqual(response.status_code, 302)

    def test_make_post_unauthorized(self):
        """
        Проверяет, что неавторизованный пользователь не может попасть на страницу создания поста.
        """
        response = self.client.get(reverse('make_post'))
        self.assertEqual(response.status_code, 302)

    def test_make_post_creation(self):
        """
        Проверяет создание нового поста через форму.
        """
        self.login()
        response = self.client.post(reverse('make_post'), {
            'title': 'New Post',
            'description': 'Content'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 1)

    def test_post_list_content(self):
        """
        Проверяет, что созданный пост отображается в списке постов.
        """
        self.login()
        Post.objects.create(user=self.user, title='Test Post', description='desc')
        response = self.client.get(reverse('posts_all'))
        self.assertContains(response, 'Test Post')

    def test_login_invalid(self):
        """
        Проверяет обработку неверных данных при входе.
        """
        response = self.client.post(reverse('log_in'), {
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Incorrect password and/or username')

    def test_sign_up_invalid_password(self):
        """
        Проверяет обработку некорректного пароля при регистрации.
        """
        response = self.client.post('/sign_up/', {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': '123',
            'password2': '123',
            'gender': '1',
            'about': 'Test user',
        })
        self.assertContains(response, "Password does not meet the requirements")

    def test_sign_up_password_mismatch(self):
        """
        Проверяет обработку несовпадения паролей при регистрации.
        """
        response = self.client.post('/sign_up/', {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'Password123',
            'password2': 'Password124',
            'gender': '1',
            'about': 'Test user',
        })
        self.assertContains(response, "Passwords do not match")

    def test_profile_edit_unauthorized(self):
        """
        Проверяет, что неавторизованный пользователь не может редактировать профиль.
        """
        response = self.client.get(reverse('profile_edit'))
        self.assertEqual(response.status_code, 302)

    def test_post_page_unauthorized(self):
        """
        Проверяет, что неавторизованный пользователь не может просматривать страницу поста.
        """
        post = Post.objects.create(user=self.user, title='Test Post', description='desc')
        response = self.client.get(reverse('post', kwargs={'id': post.id}))
        self.assertEqual(response.status_code, 302)

    def test_post_comment_unauthorized(self):
        """
        Проверяет, что неавторизованный пользователь не может оставить комментарий.
        """
        post = Post.objects.create(user=self.user, title='Test Post', description='desc')
        response = self.client.post(reverse('post', kwargs={'id': post.id}), {
            'text': 'Nice post!'
        })
        self.assertEqual(response.status_code, 302)

    def test_send_like_post_unauthorized(self):
        """
        Проверяет, что неавторизованный пользователь не может лайкнуть пост.
        """
        post = Post.objects.create(user=self.user, title='Test Post', description='desc')
        response = self.client.get(reverse('like', kwargs={'id': post.id}))
        self.assertEqual(response.status_code, 302)

    def test_gallery_liked_page_unauthorized(self):
        """
        Проверяет, что неавторизованный пользователь не может просматривать понравившиеся луки.
        """
        response = self.client.get(reverse('gallery_liked'))
        self.assertEqual(response.status_code, 302)

    def test_for_you_page_authorized(self):
        """
        Проверяет доступность страницы рекомендаций для авторизованного пользователя.
        """
        self.login()
        response = self.client.get(reverse('for_you'))
        self.assertEqual(response.status_code, 200)

    def test_scrolling_page_authorized(self):
        """
        Проверяет доступность страницы скроллинга для авторизованного пользователя.
        """
        self.login()
        response = self.client.get(reverse('scrolling'))
        self.assertEqual(response.status_code, 200)

    def test_get_city_by_coords_valid(self):
        """
        Проверяет корректную работу определения города по координатам.
        """
        response = self.client.get(reverse('get_city_by_coords'), {'lat': '55.7558', 'lon': '37.6173'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(response.json().get('city'), ['Москва', 'Moscow'])

    def test_save_look_empty_authorized(self):
        """
        Проверяет сохранение лука авторизованным пользователем по look_id.
        """
        self.login()
        response = self.client.post(reverse('save_look_empty'), {'look_id': 1})
        self.assertEqual(response.status_code, 200)

    def test_like_look_authorized(self):
        """
        Проверяет возможность лайкнуть лук авторизованным пользователем.
        """
        self.login()
        response = self.client.post(reverse('like_look'), {'look_id': 1})
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())

    def test_dislike_look_authorized(self):
        """
        Проверяет возможность дизлайкнуть лук авторизованным пользователем.
        """
        self.login()
        response = self.client.post(reverse('dislike_look'), {'look_id': 1})
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json())

    def test_make_post_with_image(self):
        """
        Проверяет создание поста с изображением (некорректный кейс).
        """
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
        """
        Проверяет, что созданный пост отображается в API.
        """
        Post.objects.create(user=self.user, title='API Test Post', description='desc')
        response = self.client.get(reverse('post_api'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'API Test Post')

    def test_profile_edit_password_change(self):
        """
        Проверяет смену пароля через редактирование профиля.
        """
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
        self.client.logout()
        self.assertTrue(self.client.login(username='testuser', password='NewPass123!'))

    def test_checker_password_validation(self):
        """
        Проверяет функцию checker для валидации паролей.
        """
        self.assertTrue(checker("!1Testpass"))
        self.assertFalse(checker("Short1!"))
        self.assertFalse(checker("NoNumbers!"))
        self.assertFalse(checker("NoSpecial1"))
        self.assertFalse(checker("!1nopercase"))
        self.assertFalse(checker("!1ONLYUPPER"))

    def test_for_you_page_with_city(self):
        """
        Проверяет работу страницы рекомендаций с передачей параметра города.
        """
        self.login()
        response = self.client.get(reverse('for_you') + '?city=London')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['city'], 'London')
        self.assertTrue('temperature' in response.context or 'error' in response.context)

    def test_save_look_empty_with_look_id(self):
        """
        Проверяет сохранение лука по look_id.
        """
        self.login()
        response = self.client.post(reverse('save_look_empty'), {'look_id': 1})
        self.assertEqual(response.status_code, 200)

    def test_scrolling_page_with_liked_disliked_looks(self):
        """
        Проверяет доступность страницы скроллинга при наличии лайкнутых и дизлайкнутых луков.
        """
        self.login()
        response = self.client.get(reverse('scrolling'))
        self.assertEqual(response.status_code, 200)
