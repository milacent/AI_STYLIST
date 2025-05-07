from django.contrib import messages
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseServerError, HttpResponseRedirect, JsonResponse
from django.urls import path, reverse
from django.contrib.auth.decorators import login_required
from final_project_app.models import Info, Comment, Post, LikePost, LikeComment, Looks, LikedLook, DislikedLook
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import PostForm
from .models import get_current_weather

# Create your views here.

def Handle400(request, exception = None):
    context = {}
    print(request.path)
    if not request.path.endswith('/'):
        return HttpResponseRedirect(request.path + '/')
    return render(request, "Handle/Error400.html", context)

def index_page(request):
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
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("profile", username=user.username)
        else:
            context['error'] = "Invalid username or password"
            print('1')

    return render(request, "auth/log_in.html", context)

def posts_api(request):
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


def sign_up_page(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        password2 = request.POST['password2']
        gender = request.POST['gender']
        about_me = request.POST['about']
        if password == password2:
            user = User.objects.create_user(username, email, password)
            info = Info(user=user,
                        gender=int(gender), about_me=about_me)
            user.save()
            info.save()
            logout(request)
            return redirect('/log_in')
    return render(request, "auth/sign_up.html", context)


@login_required
def profile_page(request, username=None):
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
                'title': '⭐ Сохранённые образы',
                'looks': request.user.saved_looks.all()[:4],
                'status': 'saved',
                'view_all_url': 'view_all_saved'
            },
            {
                'title': '❤️ Понравившиеся образы',
                'looks': Looks.objects.filter(likedlook__user=request.user)[:4],
                'status': 'liked',
                'view_all_url': 'view_all_liked'
            },
            {
                'title': '💔 Не понравившиеся образы',
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
    if request.method == 'POST':
        look = get_object_or_404(Looks, id=look_id)
        request.user.saved_looks.remove(look)
        messages.success(request, 'Образ удалён из сохранённых')
        if request.POST.get('source') == 'view_all':
            return redirect('view_all_saved')
        return redirect('profile', username=request.user.username)
    return redirect('profile', username=request.user.username)

@login_required
def view_all_saved(request):
    looks = request.user.saved_looks.all()
    return render(request, 'profile/view_all.html', {
        'looks': looks,
        'title': 'Все сохранённые образы',
        'status': 'saved'
    })

@login_required
def view_all_liked(request):
    looks = Looks.objects.filter(likedlook__user=request.user)
    return render(request, 'profile/view_all.html', {
        'looks': looks,
        'title': 'Все понравившиеся образы',
        'status': 'liked'
    })

@login_required
def view_all_disliked(request):
    looks = Looks.objects.filter(dislikedlook__user=request.user)
    return render(request, 'profile/view_all.html', {
        'looks': looks,
        'title': 'Все не понравившиеся образы',
        'status': 'disliked'
    })

@login_required
def gallery_liked_page(request):
    liked_posts = Post.objects.filter(likepost__user=request.user)
    context = {
        'liked_posts': liked_posts
    }
    return render(request, "profile/gallery_liked.html", context)

@login_required
def profile_edit_page(request):
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
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect(reverse('posts_all'))
    else:
        form = PostForm()

    return render(request, 'outfits/make_post.html', {'form': form})

@login_required
def post_list(request):
    posts = Post.objects.all()
    return render(request, 'outfits/posts_all.html', {'posts': posts})

@login_required
def post_page(request, id=0):
    print(id)
    post = Post.objects.get(id=id)
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
    context = {}
    return render(request, 'outfits/catalog.html', context)


def about_page(request):
    context = {}
    return render(request, "info/about.html", context)

def terms_page(request):
    context = {}
    return render(request, "general/terms.html", context)

@login_required
def for_you_page(request):
    city = request.GET.get('city', 'Moscow')
    error = None
    look = None
    temperature = None

    try:
        temperature = get_current_weather(city)
        if temperature is None:
            raise ValueError("Не удалось получить данные о погоде")

        print(f"[INFO] Текущая погода в городе {city}: {temperature}°C")
        look = Looks.get_for_temperature(temperature)
        if not look:
            raise ValueError("Не найдены подходящие образы для этой температуры")

    except Exception as e:
        error = str(e)

    context = {
        'look': look,
        'temperature': temperature,
        'city': city,
        'error': error
    }
    return render(request, 'outfits/for_you.html', context)

@login_required
def save_look_empty(request):
    if request.method == 'POST':
        look_id = request.POST.get('look_id')
        if not look_id:
            return render(request, 'outfits/for_you.html', {
                'error': "Не удалось определить образ для сохранения.",
                'look': None
            })
        try:
            look = Looks.objects.get(id=look_id)
            request.user.saved_looks.add(look)
            return redirect('for_you')
        except Looks.DoesNotExist:
            return render(request, 'outfits/for_you.html', {
                'error': "Образ не найден.",
                'look': None
            })
        except Exception as e:
            return render(request, 'outfits/for_you.html', {
                'error': f"Ошибка сохранения: {str(e)}",
                'look': None
            })
    return redirect('for_you')


@login_required
def scrolling_page(request):
    liked_look_ids = LikedLook.objects.filter(user=request.user).values_list('look_id', flat=True)
    disliked_look_ids = DislikedLook.objects.filter(user=request.user).values_list('look_id', flat=True)
    excluded_ids = list(liked_look_ids) + list(disliked_look_ids)

    looks = Looks.objects.exclude(id__in=excluded_ids).order_by('?')[:5]

    context = {
        'looks': looks,
        'error': None if looks else "Не найдено ни одного нового образа"
    }
    return render(request, 'outfits/scrolling.html', context)


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
            return JsonResponse({'city': city})
        else:
            return JsonResponse({'error': 'City not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)