from django.contrib import messages
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Info, Comment, Post, LikePost, Looks, LikedLook, DislikedLook
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import PostForm
from .models import get_current_weather
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from .utils import *
from .look_factory import LookFactory
import logging
logger = logging.getLogger(__name__)

# Create your views here.

def Handle400(request, exception = None):
    """
        Обработчик ошибки 400 (Bad Request).

        Args:
            request (HttpRequest): Объект запроса
            exception (Exception): Исключение, вызвавшее ошибку

        Returns:
            HttpResponseRedirect или HttpResponse: Редирект или страница ошибки
        """
    context = {}
    print(request.path)
    if not request.path.endswith('/'):
        return HttpResponseRedirect(request.path + '/')
    return render(request, "Handle/Error400.html", context)

def index_page(request):
    """
        Главная страница приложения. Отображает самый популярный пост по количеству лайков.

        Args:
            request (HttpRequest): Объект запроса

        Returns:
            HttpResponse: Рендер главной страницы с контекстом:
                - top_post: Самый популярный пост
                - max_likes: Количество лайков топового поста
        """
    top_post = None
    max_likes = -1

    for post in Post.objects.all():
        likes_count = LikePost.objects.filter(post=post).count()
        if likes_count > max_likes:
            max_likes = likes_count
            top_post = post

    context = {
        'top_post': top_post,
        'max_likes': max_likes if max_likes != -1 else 0,
    }
    return render(request, "general/index.html", context)

def log_out(request):
    """Выход из аккаунта пользователя"""
    logout(request)
    return redirect('index')

def log_in_page(request):
    """
        Страница авторизации пользователя.

        Обрабатывает POST-запрос с данными для входа:
        - username: Логин пользователя
        - password: Пароль

        При успешной аутентификации перенаправляет на страницу профиля.
        """
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("profile", username=user.username)
        elif username != '' and password != '':
            messages.add_message(request, messages.ERROR,'Incorrect password and/or username')

    return render(request, "auth/log_in.html", context)

def posts_api(request):
    """
        API-эндпоинт для получения списка постов в формате JSON.

        Returns:
            JsonResponse: Список постов с полями:
                - id: Идентификатор поста
                - title: Заголовок
                - image: URL изображения
                - description: Текст поста
        """
    posts = Post.objects.all()
    data = [
        {
            'id': post.id,
            'title': post.title,
            'image': post.image.url if post.image else '',
            'description': post.description
        }
        for post in posts
    ]
    return JsonResponse(data, safe=False)

def checker(string):
    """
        Валидатор сложности пароля.

        Проверяет, что пароль содержит:
        - Минимум 8 символов
        - Хотя бы одну заглавную и строчную букву
        - Хотя бы одну цифру
        - Хотя бы один специальный символ

        Args:
            string (str): Пароль для проверки

        Returns:
            bool: Результат проверки
        """
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lower = upper.lower()
    numbers = '1234567890'
    special = '!@#$%^&*()_+/?.,:;[]}{<>'
    if len(string) < 8:
        return False
    up = 0
    low = 0
    num = 0
    sp = 0
    for char in string:
        if char in upper:
            up += 1
        elif char in lower:
            low += 1
        elif char in numbers:
            num += 1
        elif char in special:
            sp += 1
        else:
            return False

    if up < 1 or low < 1 or num < 1 or sp < 1:
        return False
    return True

def sign_up_page(request):
    """
        Страница регистрации нового пользователя.

        Обрабатывает POST-запрос с данными:
        - username: Логин
        - email: Email
        - password1: Пароль
        - password2: Подтверждение пароля
        - gender: Пол (1-мужской, 2-женский)
        - about: О себе

        Создает нового пользователя и связанную информацию профиля.
    """
    context = {}

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        password2 = request.POST['password2']
        gender = request.POST['gender']
        about_me = request.POST['about']

        # Проверка совпадения паролей
        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, "auth/sign_up.html", context, status=200)

        # Проверка соблюдения требований к паролю
        if not checker(password):
            messages.error(request, 'Password does not meet the requirements')
            return render(request, "auth/sign_up.html", context, status=200)

        try:
            # Создание пользователя
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            # Создание профиля пользователя
            info = Info(user=user, gender=int(gender), about_me=about_me)
            info.save()

            # После успешной регистрации, logout текущего пользователя (если он был авторизован)
            logout(request)
            return redirect('/log_in')
        except Exception as e:
            # Обработка ошибок (например, если имя пользователя или email уже существует)
            messages.error(request, f"Error: {str(e)}")
            return render(request, "auth/sign_up.html", context, status=200)

    return render(request, "auth/sign_up.html", context)


@login_required
def profile_page(request, username=None):
    """
       Страница профиля пользователя.

       Args:
           request (HttpRequest): Объект запроса
           username (str): Имя пользователя (опционально)

       Returns:
           HttpResponse: Рендер страницы профиля с контекстом:
               - profile_user: Объект пользователя
               - info: Дополнительная информация профиля
               - is_own_profile: Флаг принадлежности профиля
               - user_posts: Посты пользователя
               - look_sections: Секции с образами
               - liked_posts: Понравившиеся посты
       """
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = (request.user == profile_user)

    try:
        info = Info.objects.get(user=profile_user)
    except Info.DoesNotExist:
        info = None

    # Получаем посты пользователя
    user_posts = Post.objects.filter(user=profile_user).order_by('-id')

    # Для своего профиля показываем сохраненные образы
    if is_own_profile:
        look_sections = [
            {
                'title': '⭐ Saved Looks',
                'looks': request.user.saved_looks.all()[:4],
                'status': 'saved',
                'view_all_url': 'view_all_saved'
            },
            {
                'title': '❤️ Liked Looks',
                'looks': Looks.objects.filter(likedlook__user=request.user)[:4],
                'status': 'liked',
                'view_all_url': 'view_all_liked'
            },
            {
                'title': '💔 Disliked Looks',
                'looks': Looks.objects.filter(dislikedlook__user=request.user)[:4],
                'status': 'disliked',
                'view_all_url': 'view_all_disliked'
            }]

        liked_posts = Post.objects.filter(likepost__user=request.user)[:4]
    else:
        look_sections = []
        liked_posts = []

    context = {
        'profile_user': profile_user,
        'info': info,
        'is_own_profile': is_own_profile,
        'user_posts': user_posts,
        'look_sections': look_sections,
        'liked_posts': liked_posts,
    }
    return render(request, "profile/profile.html", context)

@login_required
def unsave_look(request, look_id):
    """
        Удаление образа из сохраненных.

        Args:
            request (HttpRequest): Объект запроса
            look_id (int): ID образа

        Returns:
            HttpResponseRedirect: Редирект на страницу профиля
        """
    if request.method == 'POST':
        look = get_object_or_404(Looks, id=look_id)
        request.user.saved_looks.remove(look)
        messages.success(request, 'Look is deleted from Saved')
        if request.POST.get('source') == 'view_all':
            return redirect('view_all_saved')
        return redirect('profile',request.user)
    return redirect('profile', request.user)

@login_required
def view_all_saved(request):
    """
        Просмотр всех сохраненных образов.

        Returns:
            HttpResponse: Рендер страницы со всеми сохраненными образами
        """
    looks = request.user.saved_looks.all()
    return render(request, 'profile/view_all.html', {
        'looks': looks,
        'title': 'Saved Looks',
        'status': 'saved'
    })

@login_required
def view_all_liked(request):
    """
        Просмотр всех понравившихся образов.

        Returns:
            HttpResponse: Рендер страницы с понравившимися образами
        """
    looks = Looks.objects.filter(likedlook__user=request.user)
    return render(request, 'profile/view_all.html', {
        'looks': looks,
        'title': 'Liked Looks',
        'status': 'liked'
    })

@login_required
def view_all_disliked(request):
    """
        Просмотр всех не понравившихся образов.

        Returns:
            HttpResponse: Рендер страницы с не понравившимися образами
        """
    looks = Looks.objects.filter(dislikedlook__user=request.user)
    return render(request, 'profile/view_all.html', {
        'looks': looks,
        'title': 'Disliked Looks',
        'status': 'disliked'
    })

@login_required
def gallery_liked_page(request):
    """
        Галерея понравившихся постов.

        Returns:
            HttpResponse: Рендер страницы с лайкнутыми постами
        """
    liked_posts = Post.objects.filter(likepost__user=request.user)
    context = {
        'liked_posts': liked_posts
    }
    return render(request, "profile/gallery_liked.html", context)

@login_required
def profile_edit_page(request):
    """
        Страница редактирования профиля.

        Обрабатывает обновление данных пользователя:
        - Логин
        - Email
        - Пароль
        - Пол
        - О себе
        """
    context = {}
    context['info'] = Info.objects.get(user=request.user)
    user = request.user
    if request.method == 'POST':
        user.username = request.POST['username']
        user.email = request.POST['email']
        try:
            if request.POST['password1'] == request.POST['password2']:
                user.set_password(request.POST['password1'])
            user.save()
            info = Info.objects.get(user=user)
            info.gender = int(request.POST['gender'])
            info.about_me = request.POST['about']
            info.save()
            login(request, user)
            return redirect('profile', username=request.user.username)
        except:
            raise SystemError

    return render(request, "profile/profile_edit.html", context)

@login_required
def make_post_page(request):
    """
        Страница создания нового поста.
        Использует PostForm для валидации данных.
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)

        # Проверка валидности формы
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user  # Привязка поста к текущему пользователю
            post.save()
            return redirect(reverse('posts_all'))  # Редирект после успешного сохранения

        else:
            # Ошибка формы, рендерим страницу с ошибками
            print(form.errors)
            return render(request, 'outfits/make_post.html', {'form': form})

    else:
        form = PostForm()

    return render(request, 'outfits/make_post.html', {'form': form})


@login_required
def post_list(request):
    """
       Список всех постов в системе.

       Returns:
           HttpResponse: Рендер страницы со всеми постами
       """
    posts = Post.objects.all()
    return render(request, 'outfits/posts_all.html', {'posts': posts})

@login_required
def post_page(request, id=0):
    """
        Страница просмотра отдельного поста.

        Args:
            id (int): ID поста

        Returns:
            HttpResponse: Рендер страницы поста с комментариями
        """
    print(id)
    post = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        comment = Comment(user=request.user, content=request.POST['text'], post=post)
        comment.save()
    context = {
        'id':id,
        'author':post.user,
        'title':post.title,
        'description':post.description,
        'image':post.image,
        'likes':len(LikePost.objects.filter(post=post)),
        'comments':Comment.objects.filter(post=post),
    }
    return render(request, "outfits/post.html", context)


@login_required
def send_like_post(request, id):
    """
        Обработка лайка/дизлайка поста.

        Args:
            id (int): ID поста

        Returns:
            HttpResponseRedirect: Редирект на предыдущую страницу
        """
    post = get_object_or_404(Post, id=id)
    like = LikePost.objects.filter(user=request.user, post=post)

    # Определяем откуда пришел запрос
    referer = request.META.get('HTTP_REFERER', '')

    next_page = request.GET.get('next')

    if like.exists():
        like.delete()
        if next_page == 'gallery_liked':
            return redirect('gallery_liked')
        elif 'gallery_liked' in referer:
            return redirect('gallery_liked')
        # По умолчанию остаемся на текущей странице
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('post', args=[post.id])))
    else:
        LikePost.objects.create(user=request.user, post=post)
        return redirect('post', post.id)


@login_required
def catalog_page(request):
    """Страница каталога образов."""
    context = {}
    return render(request, 'outfits/catalog.html', context)


def about_page(request):
    """Страница 'О проекте'."""
    context = {}
    return render(request, "info/about.html", context)

def terms_page(request):
    """Страница с пользовательским соглашением."""
    context = {}
    return render(request, "general/terms.html", context)

@login_required
def for_you_page(request, city):
    """
    Персональные рекомендации образов на основе погоды.

    Используется паттерн проектирования "Фабрика" (Factory) для выбора стратегии подбора образа
    в зависимости от критерия (в данном случае - температуры).

    Args:
        city (str): Город для погодного запроса, передаётся через GET-параметр 'city'. По умолчанию 'Moscow'.

    Returns:
        HttpResponse: Рендер страницы с рекомендованным образом, температурой, городом и возможной ошибкой.
    """
    error = None
    look = None
    temperature = None
    conditions = None

    try:
        temperature = get_current_weather(city)
        conditions = get_weather_conditions(city)
        if temperature is None:
            raise ValueError("No data about weather")

        print(f"[INFO] Текущая погода в городе {city}: {temperature}°C, состояние: {conditions}")
        strategy = LookFactory.get_strategy("temperature")
        look = strategy.get_look(temperature=temperature)
        if not look:
            raise ValueError("No Looks for this weather")

    except Exception as e:
        error = str(e)

    include_templates = {
        'ясно': 'weather/sun.html',
        'облачно': 'weather/clouds.html',
        'дождь': 'weather/rain.html',
        'снег': 'weather/snow.html',
    }
    weather_template = include_templates.get(conditions, None)

    context = {
        'look': look,
        'temperature': temperature,
        'conditions': conditions,
        'city': city,
        'error': error,
        'weather_template': weather_template
    }
    return render(request, 'outfits/for_you.html', context)

@login_required
def save_look_empty(request):
    """
        Сохранение рекомендованного образа.

        Args:
            look_id (int): ID сохраняемого образа

        Returns:
            HttpResponseRedirect: Редирект на страницу рекомендаций
        """
    if request.method == 'POST':
        look_id = request.POST.get('look_id')
        if not look_id:
            return render(request, 'outfits/for_you.html', {
                'error': "Couldn't identify the Look to save",
                'look': None
            })
        try:
            look = Looks.objects.get(id=look_id)
            request.user.saved_looks.add(look)
            return redirect('for_you')
        except Looks.DoesNotExist:
            return render(request, 'outfits/for_you.html', {
                'error': "Look was not found",
                'look': None
            })
        except Exception as e:
            return render(request, 'outfits/for_you.html', {
                'error': f"Saving error: {str(e)}",
                'look': None
            })
    return redirect('for_you')

@login_required
def scrolling_page(request):
    """
        Лента рекомендаций образов с учетом предпочтений.

        Использует алгоритмы машинного обучения для подбора образов:
        - Анализ лайков/дизлайков
        - Расчет косинусной близости векторов
        """

    # Получаем ID лайков и дизлайков
    liked_look_ids = LikedLook.objects.filter(user=request.user).values_list('look_id', flat=True)
    disliked_look_ids = DislikedLook.objects.filter(user=request.user).values_list('look_id', flat=True)
    excluded_ids = list(liked_look_ids) + list(disliked_look_ids)

    # Получаем вектора понравившихся образов
    user_dislike_vectors, user_like_vectors = find_liked_disliked(disliked_look_ids, liked_look_ids)

    if not user_like_vectors and not user_dislike_vectors:
        # Показываем 5 случайных образов, если нет лайков и дизлайков
        looks = Looks.objects.exclude(id__in=excluded_ids).order_by('?')[:10]
    else:
        user_like_vector = None
        user_dislike_vector = None
        has_likes = bool(user_like_vectors)
        has_dislikes = bool(user_dislike_vectors)

        if has_likes:
            user_like_vector = np.mean(np.array(user_like_vectors), axis=0).reshape(1, -1)
        if has_dislikes:
            user_dislike_vector = np.mean(np.array(user_dislike_vectors), axis=0).reshape(1, -1)

        candidate_looks = Looks.objects.exclude(id__in=excluded_ids)
        scored_looks = []

        get_vector(candidate_looks, has_dislikes, has_likes, scored_looks, user_dislike_vector, user_like_vector)

        filtered_looks = [(look, score) for look, score in scored_looks if score > 0.6]
        filtered_looks.sort(key=lambda x: x[1], reverse=True)
        looks = [look for look, score in filtered_looks[:10]]

        # Если нет хороших совпадений — fallback на случайные
        if not looks:
            looks = Looks.objects.exclude(id__in=excluded_ids).order_by('?')[:10]


    context = {
        'looks': looks,
        'error': None if looks else "No Looks found"
    }
    return render(request, 'outfits/scrolling.html', context)


def find_liked_disliked(disliked_look_ids, liked_look_ids):
    """
        Извлекает векторные представления лайкнутых и дизлайкнутых образов.

        Args:
            disliked_look_ids (QuerySet): ID дизлайкнутых образов
            liked_look_ids (QuerySet): ID лайкнутых образов

        Returns:
            tuple: Кортеж содержащий:
                - user_dislike_vectors (list): Вектора дизлайкнутых образов
                - user_like_vectors (list): Вектора лайкнутых образов
        """
    liked_looks = Looks.objects.filter(id__in=liked_look_ids)
    user_like_vectors = []
    for look in liked_looks:
        try:
            vec = json.loads(look.general_vector)
            user_like_vectors.append(vec)
        except:
            continue

    # Получаем вектора не понравившихся образов
    disliked_looks = Looks.objects.filter(id__in=disliked_look_ids)
    user_dislike_vectors = []
    for look in disliked_looks:
        try:
            vec = json.loads(look.general_vector)
            user_dislike_vectors.append(vec)
        except:
            continue
    return user_dislike_vectors, user_like_vectors


def get_vector(candidate_looks, has_dislikes, has_likes, scored_looks, user_dislike_vector, user_like_vector):
    """
        Обработчик лайка образа через AJAX.

        Args:
            request (HttpRequest): POST-запрос с параметром look_id

        Returns:
            JsonResponse: Результат операции:
                - status: success/error
                - message: Сообщение об ошибке (при наличии)
    """
    for look in candidate_looks:
        try:
            vec = np.array(json.loads(look.general_vector)).reshape(1, -1)
            sim_liked = cosine_similarity(user_like_vector, vec)[0][0] if has_likes else 0
            sim_disliked = cosine_similarity(user_dislike_vector, vec)[0][0] if has_dislikes else 0

            alpha = 0.8
            final_score = sim_liked - alpha * sim_disliked
            scored_looks.append((look, final_score))
        except:
            continue


@login_required
def like_look(request):
    if request.method == 'POST':
        look_id = request.POST.get('look_id')
        try:
            look = Looks.objects.get(id=look_id)
            LikedLook.objects.get_or_create(user=request.user, look=look)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid request'})


@login_required
def dislike_look(request):
    """
        Обработчик дизлайка образа через AJAX.

        Args:
            request (HttpRequest): POST-запрос с параметром look_id

        Returns:
            JsonResponse: Результат операции:
                - status: success/error
                - message: Сообщение об ошибке (при наличии)
        """
    if request.method == 'POST':
        look_id = request.POST.get('look_id')
        try:
            look = Looks.objects.get(id=look_id)
            DislikedLook.objects.get_or_create(user=request.user, look=look)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid request'})

def get_city_by_coords(request):
    """
        Определение города по географическим координатам через OpenStreetMap API.

        Args:
            request (HttpRequest): GET-запрос с параметрами:
                - lat: Широта
                - lon: Долгота

        Returns:
            JsonResponse: Результат с названием города или ошибкой:
            JsonResponse: Результат с названием города или ошибкой:
                - city: Название города (при успехе)
                - error: Сообщение об ошибке (при неудаче)
        """
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    if not lat or not lon:
        return JsonResponse({'error': 'Missing coordinates'}, status=400)

    try:
        url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}'
        response = requests.get(url, headers={'User-Agent': 'final_project_app'})
        data = response.json()
        city = data.get('address', {}).get('city') or data.get('address', {}).get('town') or data.get('address', {}).get('village')
        if city:
            return JsonResponse({'city': city}, status=200)
        else:
            return JsonResponse({'error': 'City not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def for_you_redirect(request):
    return redirect('for_you', city='Moscow')
