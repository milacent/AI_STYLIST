from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseServerError, HttpResponseRedirect, JsonResponse
from django.urls import path, reverse

from django.contrib.auth.decorators import login_required
from final_project_app.models import Info, Comment, Post, LikePost, LikeComment, Looks
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from .models import Post
from .forms import PostForm

from django.contrib.auth import login, authenticate, logout
import requests

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
            return redirect(f"/profile/{user.username}/")
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
        gender = request.POST['gender']
        about_me = request.POST['about']

        if password == password2:
            user = User.objects.create_user(username, email, password)
            info = Info(user=user, gender=int(gender), about_me=about_me)
            user.save()
            info.save()
            logout(request)
            return redirect('/log_in')
    return render(request, "auth/sign_up.html", context)


@login_required
def profile_page(request, username):
    context = {}
    user_obj = get_object_or_404(User, username=username)
    context['profile_user'] = user_obj 
    context['info'] = Info.objects.get(user=user_obj)
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
            info.gender = int(request.POST['gender'])
            info.about_me = request.POST['about']
            info.save()
            login(request, user)
            return redirect(f"/profile/{user.username}/")
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
def profile_redirect(request):
    return redirect(f'/profile/{request.user.username}/')

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


@login_required
def view_all_saved(request):
    context = {}
    # Показать все образы
    context['looks'] = Looks.objects.all()
    return render(request, "profile/saved_looks.html", context)

@login_required
def view_all_liked(request):
    context = {}
    # Показать образы из теплого диапазона (их можно лайкнуть)
    context['looks'] = Looks.objects.filter(temp_range__in=['20_30', '10_20']).order_by('?')
    return render(request, "profile/liked_looks.html", context)

@login_required
def view_all_disliked(request):
    context = {}
    # Показать образы из холодного диапазона (их можно дизлайкнуть)
    context['looks'] = Looks.objects.filter(temp_range__in=['-20_-10', '-10_0']).order_by('?')
    return render(request, "profile/disliked_looks.html", context)

def scrolling_page(request):
    context = {}
    # Получить случайные образы
    looks = Looks.objects.all().order_by('?')[:50]
    context['looks'] = list(looks)
    return render(request, "outfits/scrolling.html", context)

def about_page(request):
    context = {}
    return render(request, "info/about.html", context)

def terms_page(request):
    context = {}
    return render(request, "general/terms.html", context)

def get_weather_template(city):
    """Получить погоду через Open-Meteo API (бесплатный, без регистрации)"""
    
    print(f"\n[DEBUG] === WEATHER REQUEST ===")
    print(f"[DEBUG] City: {city}")
    
    # Маппинг названий городов на координаты (самые крупные)
    city_coords = {
        'moscow': (55.7558, 37.6173),
        'saint petersburg': (59.9311, 30.3609),
        'novosibirsk': (55.0415, 82.8979),
        'yekaterinburg': (56.8389, 60.6057),
        'kazan': (55.7887, 49.1221),
    }
    
    coords = city_coords.get(city.lower())
    if not coords:
        print(f"[ERROR] City not found in database: {city}")
        return 'weather/clouds.html'
    
    lat, lon = coords
    print(f"[DEBUG] Coordinates: {lat}, {lon}")
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=weather_code,temperature_2m&temperature_unit=celsius"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"[DEBUG] Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[ERROR] API error: {response.status_code}")
            return 'weather/clouds.html'
        
        data = response.json()
        print(f"[DEBUG] Response: {data}")
        
        weather_code = data.get('current', {}).get('weather_code')
        temp = data.get('current', {}).get('temperature_2m')
        
        print(f"[DEBUG] Weather code: {weather_code}, Temp: {temp}°C")
        
        # WMO Weather interpretation codes
        # 0 = Clear sky
        # 1,2 = Mainly clear, partly cloudy
        # 3 = Overcast
        # 45,48 = Foggy
        # 51-67 = Drizzle, rain
        # 71-86 = Snow
        
        if weather_code == 0:
            print(f"[INFO] → sun.html (clear)")
            return 'weather/sun.html'
        elif weather_code in [1, 2]:
            print(f"[INFO] → clouds.html (partly cloudy)")
            return 'weather/clouds.html'
        elif weather_code in [3]:
            print(f"[INFO] → clouds.html (overcast)")
            return 'weather/clouds.html'
        elif weather_code in [45, 48]:
            print(f"[INFO] → clouds.html (fog)")
            return 'weather/clouds.html'
        elif weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            print(f"[INFO] → rain.html (drizzle/rain)")
            return 'weather/rain.html'
        elif weather_code in [71, 73, 75, 77, 85, 86]:
            print(f"[INFO] → snow.html (snow)")
            return 'weather/snow.html'
        else:
            print(f"[INFO] → clouds.html (unknown code)")
            return 'weather/clouds.html'
            
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
        return 'weather/clouds.html'
        print(f"Weather API error: {e}")
        return 'weather/clouds.html'

def get_look_by_temperature(temperature):
    """Получить случайный образ"""
    look = Looks.objects.all().order_by('?').first()
    return look


def get_temperature_for_city(city):
    api_key = '5877dfece4965cb516686773acae60b7'
    try:
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}",
            timeout=5
        )
        data = response.json()
        if response.status_code == 200:
            return data['main']['temp']
        else:
            return 15 
    except Exception:
        return 15

def get_city_coordinates(city):
    """Получить координаты города"""
    city_coords = {
        'moscow': (55.7558, 37.6173),
        'saint petersburg': (59.9311, 30.3609),
        'novosibirsk': (55.0415, 82.8979),
        'yekaterinburg': (56.8389, 60.6057),
        'kazan': (55.7887, 49.1221),
    }
    coords = city_coords.get(city.lower())
    return coords if coords else (55.7558, 37.6173)

def get_weather_by_coords(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=weather_code&temperature_unit=celsius"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return 'weather/clouds.html'
        
        data = response.json()
        weather_code = data.get('current', {}).get('weather_code')
        
        if weather_code == 0:
            return 'weather/sun.html'
        elif weather_code in [1, 2, 3, 45, 48]:
            return 'weather/clouds.html'
        elif weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            return 'weather/rain.html'
        elif weather_code in [71, 73, 75, 77, 85, 86]:
            return 'weather/snow.html'
        return 'weather/clouds.html'
    except:
        return 'weather/clouds.html'


def get_city_by_coords(request):
    """Получить ближайший город по координатам и вернуть JSON"""
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    
    print(f"\n[DEBUG] get_city_by_coords - lat: {lat}, lon: {lon}")
    
    if not lat or not lon:
        return JsonResponse({'city': 'Moscow', 'error': 'Координаты не получены'})
    
    try:
        # Используем Open-Meteo для обратного геокодирования (очень медленно)
        # Вместо этого сопоставим координаты с ближайшим городом
        lat = float(lat)
        lon = float(lon)
        
        city_coords = {
            'Moscow': (55.7558, 37.6173),
            'Saint Petersburg': (59.9311, 30.3609),
            'Novosibirsk': (55.0415, 82.8979),
            'Yekaterinburg': (56.8389, 60.6057),
            'Kazan': (55.7887, 49.1221),
        }
        
        # Найти ближайший город
        min_distance = float('inf')
        nearest_city = 'Moscow'
        
        for city, (city_lat, city_lon) in city_coords.items():
            # Простое вычисление расстояния
            distance = ((lat - city_lat) ** 2 + (lon - city_lon) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest_city = city
        
        print(f"[DEBUG] Nearest city: {nearest_city}")
        return JsonResponse({'city': nearest_city, 'error': None})
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return JsonResponse({'city': 'Moscow', 'error': str(e)})


def for_you_page(request, city=None):
    context = {}
    if not city:
        city = 'Moscow' 
    context['city'] = city

    lat, lon = get_city_coordinates(city)
    context['lat'] = lat
    context['lon'] = lon

    # Получить текущую температуру в городе
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&temperature_unit=celsius"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            temp_data = response.json()
            temperature = temp_data.get('current', {}).get('temperature_2m', 15)
            print(f"[DEBUG] Temperature in {city}: {temperature}°C")
        else:
            temperature = 15
            print(f"[DEBUG] Temperature API error, using default: 15°C")
    except Exception as e:
        temperature = 15
        print(f"[DEBUG] Temperature error: {e}, using default: 15°C")
    
    # Определить температурный диапазон
    if temperature <= -15:
        temp_range = '-20_-10'
    elif temperature <= -5:
        temp_range = '-10_0'
    elif temperature <= 5:
        temp_range = '0_10'
    elif temperature <= 15:
        temp_range = '10_20'
    else:
        temp_range = '20_30'
    
    print(f"[DEBUG] Selected temp_range: {temp_range}")
    
    # Получить образы для этого температурного диапазона
    looks = Looks.objects.filter(temp_range=temp_range).order_by('?')
    
    if looks.exists():
        look = looks.first()
        print(f"[DEBUG] Found {looks.count()} looks for {temp_range}")
    else:
        # Если нет образов для точного диапазона, взять случайный
        print(f"[DEBUG] No looks for {temp_range}, using random")
        look = Looks.objects.all().order_by('?').first()
    
    if look:
        context['look'] = look
    else:
        context['error'] = 'Образы не найдены'

    weather_template = get_weather_template(city)
    context['weather_template'] = weather_template
    
    return render(request, "outfits/for_you.html", context)

def save_look_empty(request):
    city = request.POST.get('city', 'Moscow')
    return redirect(f'/for_you/{city}/')

def log_out(request):
    """Выход из аккаунта пользователя"""
    logout(request)
    return redirect('index')
