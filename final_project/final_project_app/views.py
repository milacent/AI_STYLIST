from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseServerError, HttpResponseRedirect
from django.urls import path, reverse

from django.contrib.auth.decorators import login_required
from final_project_app.models import Info, Comment, Post, LikePost, LikeComment
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from .models import Post
from .forms import PostForm

from django.contrib.auth import login, authenticate, logout
# Create your views here.

def Handle400(request, exception = None):
    context = {}
    print(request.path)
    if not request.path.endswith('/'):
        return HttpResponseRedirect(request.path + '/')
    return render(request, "Handle/Error400.html", context)

def index_page(request):
    context = {}
    return render(request, "general/index.html", context)

def log_in_page(request):
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

def sign_up_page(request):
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
    context = {}
    context['info'] = Info.objects.get(user=request.user)
    return render(request, "profile/profile.html", context)

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
    context = {}
    # context['items'] = Items.objects.all
    return render(request, 'outfits/catalog.html', context)

@login_required
def gallery_liked_page(request):
    liked_posts = Post.objects.filter(likepost__user=request.user)
    context = {
        'liked_posts': liked_posts
    }
    return render(request, "profile/gallery_liked.html", context)


def scrolling_page(request):
    context = {}
    return render(request, "outfits/scrolling.html", context)

def about_page(request):
    context = {}
    return render(request, "info/about.html", context)

def terms_page(request):
    context = {}
    return render(request, "general/terms.html", context)

def for_you_page(request):
    context = {}
    return render(request, "outfits/for_you.html", context)

def log_out(request):
    """Выход из аккаунта пользователя"""
    logout(request)
    return redirect('index')
