from pyexpat.errors import messages
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseServerError, HttpResponseRedirect, JsonResponse
from django.urls import path, reverse
from django.contrib.auth.decorators import login_required
from final_project_app.models import Info, Comment, Post, LikePost, LikeComment, Looks, LikedLook, DislikedLook
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import PostForm
from django.contrib.auth import login, authenticate, logout
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

def Handle400(request, exception = None):
    """ handler for 404 error """
    context = {}
    print(request.path)
    if not request.path.endswith('/'):
        return HttpResponseRedirect(request.path + '/')
    return render(request, "Handle/Error400.html", context)

def index_page(request):
    """ main page """
    context = {}
    return render(request, "general/index.html", context)

def log_out(request):
    """ logout from account """
    logout(request)
    return redirect('index')

def log_in_page(request):
    """ login page
    if post request returns redirect
    else return render
    """
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/profile")
        else:
            context['error'] = "Invalid username or password"
            print('1')

    return render(request, "auth/log_in.html", context)

def posts_api(request):
    """ api for posts """
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
    """ sign up page with creation of user and optional info """
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        password2 = request.POST['password2']
        height = request.POST['height']
        weight = request.POST['weight']
        chest = request.POST['chest']
        waist = request.POST['waist']
        hips = request.POST['hips']
        gender = request.POST['gender']
        about_me = request.POST['about']
        if password == password2:
            user = User.objects.create_user(username, email, password)
            info = Info(user=user, height=int(height), weight=int(weight),
                        chest=int(chest), waist=int(waist), hips=int(hips), gender=int(gender), about_me=about_me)
            user.save()
            info.save()
            logout(request)
            return redirect('/log_in')
    return render(request, "auth/sign_up.html", context)


@login_required
def profile_page(request):
    """ profile page """
    context = {}
    context['info'] = Info.objects.get(user=request.user)
    return render(request, "profile/profile.html", context)

@login_required
def profile_edit_page(request):
    """ edit the page if request == post"""
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
            info.height = int(request.POST['height'])
            info.weight = int(request.POST['weight'])
            info.chest = int(request.POST['chest'])
            info.waist = int(request.POST['waist'])
            info.hips = int(request.POST['hips'])
            info.gender = int(request.POST['gender'])
            info.about_me = request.POST['about']
            info.save()
            login(request, user)
            return redirect('/profile')
        except:
            raise SystemError

    return render(request, "profile/profile_edit.html", context)

@login_required
def make_post_page(request):
    """ make post page
    if request == post you add the form
    """
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
    """ list all posts """
    posts = Post.objects.all()
    return render(request, 'outfits/posts_all.html', {'posts': posts})

@login_required
def post_page(request, id=0):
    """ check the post with certain id
    error not implemented
    """
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
    """ send like to certain post with id """
    context = {}
    like = LikePost.objects.filter(user=request.user, post=Post.objects.get(id=id))

    if like.exists():
        like.delete()
        return redirect('/gallery_liked')
    else:
        LikePost.objects.create(user=request.user, post=Post.objects.get(id=id))
        return redirect('/post/' + str(id))


@login_required
def catalog_page(request):
    """ catalog page """
    context = {}
    # context['items'] = Items.objects.all
    return render(request, 'outfits/catalog.html', context)

@login_required
def gallery_liked_page(request):
    """ check your liked posts and list them on a page"""
    liked_posts = Post.objects.filter(likepost__user=request.user)
    context = {
        'liked_posts': liked_posts
    }
    return render(request, "profile/gallery_liked.html", context)


def about_page(request):
    """ about page """
    context = {}
    return render(request, "info/about.html", context)

def terms_page(request):
    """ terms page """
    context = {}
    return render(request, "general/terms.html", context)

@login_required
def for_you_page(request):
    """ for you page
    WIP based on your city return different temperate and suggest other looks
    """
    city = request.GET.get('city', 'Moscow')

    try:
        look = Looks.generate_for_city(city)
        if isinstance(look, str):  # Если вернулась строка с ошибкой
            raise ValueError(look)
        look.save()

        context = {
            'look': look,
            'temperature': look.weather_grade,
            'city': city,
            'error': None
        }
    except Exception as e:
        context = {
            'error': f"Не удалось сгенерировать образ: {str(e)}",
            'look': None
        }

    return render(request, 'outfits/for_you.html', context)

# @login_required
# def save_look(request, look_id):
#     if request.method == 'POST':
#         look = Looks.objects.get(id=look_id)
#         request.user.saved_looks.add(look)
#     return redirect('for_you')

@login_required
def save_look_empty(request):
    """ save the look on for_you page """
    if request.method == 'POST':
        city = request.POST.get('city', 'Moscow')
        try:
            look = Looks.generate_for_city(city)
            if look:
                request.user.saved_looks.add(look)
                return redirect('for_you')
        except Exception as e:
            return render(request, 'outfits/for_you.html', {
                'error': f"Ошибка сохранения: {str(e)}",
                'look': None
            })
    return redirect('for_you')

# work in progress
# def regenerate_look(request):
#     city = request.GET.get('city', 'Moscow')
#     return redirect(f'/for-you/?city={city}')

@login_required
def scrolling_page(request):
    """ scrolling page """

    temp_categories = ["-20_-10", "-10_0", "0_10", "10_20", "20_30"]
    selected_category = random.choice(temp_categories)
    min_t, max_t = map(int, selected_category.split('_'))

    # Получаем ID уже оцененных образов
    liked_look_ids = LikedLook.objects.filter(user=request.user).values_list('look_id', flat=True)
    disliked_look_ids = DislikedLook.objects.filter(user=request.user).values_list('look_id', flat=True)

    looks = []
    attempts = 0
    max_attempts = 10  # Максимальное количество попыток генерации уникальных образов

    while len(looks) < 5 and attempts < max_attempts:
        look = Looks.generate_for_temperature((min_t + max_t) // 2)
        if look.head and look.top and look.bottom:
            looks.append(look)
        attempts += 1

    context = {
        'looks': looks,
        'temperature_range': f"{min_t}°C - {max_t}°C",
        'error': None if looks else "Не удалось сгенерировать новые образы для вас. Попробуйте позже."
    }
    return render(request, 'outfits/scrolling.html', context)
@login_required
def save_scrolling_look(request):
    """ save the id with certain id """
    if request.method == 'POST':
        look_id = request.POST.get('look_id')
        try:
            look = Looks.objects.get(id=look_id)
            request.user.saved_looks.add(look)
            return redirect('scrolling')
        except Exception as e:
            return render(request, 'outfits/scrolling.html', {
                'error': f"Ошибка сохранения: {str(e)}",
                'looks': []
            })
    return redirect('scrolling')

@login_required
def like_look(request):
    """ like the certain look with id """
    if request.method == 'POST':
        look_id = request.POST.get('look_id')
        try:
            look = Looks.objects.get(id=look_id)
            LikedLook.objects.get_or_create(user=request.user, look=look)
            return redirect('scrolling')
        except ObjectDoesNotExist:
            return render(request, 'outfits/scrolling.html', {
                'error': "Образ не найден",
                'looks': []
            })
        except Exception as e:
            return render(request, 'outfits/scrolling.html', {
                'error': f"Ошибка при сохранении лайка: {str(e)}",
                'looks': []
            })
    return redirect('scrolling')

@login_required
def dislike_look(request):
    """ dislike the certain look with id """
    if request.method == 'POST':
        look_id = request.POST.get('look_id')
        try:
            look = Looks.objects.get(id=look_id)
            DislikedLook.objects.get_or_create(user=request.user, look=look)
            return redirect('scrolling')
        except ObjectDoesNotExist:
            return render(request, 'outfits/scrolling.html', {
                'error': "Образ не найден",
                'looks': []
            })
        except Exception as e:
            return render(request, 'outfits/scrolling.html', {
                'error': f"Ошибка при сохранении дизлайка: {str(e)}",
                'looks': []
            })
    return redirect('scrolling')
