"""
URL configuration for final_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from final_project_app.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)

handler404 = custom_404_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_page, name='index'),
    path('api/posts/',posts_api,name='post_api'),
    path('log_in/', log_in_page, name='log_in'),
    path('sign_up/', sign_up_page, name='sign_up'),
    path('profile_edit/', profile_edit_page, name='profile_edit'),
    path('gallery_liked/', gallery_liked_page, name='gallery_liked'),
    path('unsave_look/<int:look_id>/', unsave_look, name='unsave_look'),
    path('profile/saved/', view_all_saved, name='view_all_saved'),
    path('profile/liked/', view_all_liked, name='view_all_liked'),
    path('profile/disliked/', view_all_disliked, name='view_all_disliked'),
    path('about/', about_page, name='about'),
    path('terms/', terms_page, name='terms'),
    path('for_you/', for_you_redirect, name='for_you_redirect'),
    path('for_you/', for_you_page, name='for_you'),
    path('for_you/<str:city>/', for_you_page, name='for_you'),
    path('log_out/', log_out, name='log_out'),
    path('post/<int:id>', post_page, name='post'),
    path('send_like_post/<int:id>', send_like_post, name='like'),
    # path('item/', item_page, name='items'),
    # path('item/<int:id>', item_page, name='item'),
    path('catalog/', catalog_page, name='catalog'),
    path('posts_all/', post_list, name='posts_all'),
    path('make/', make_post_page, name='make_post'),
    path('save_look/', save_look_empty, name='save_look_empty'),
    # path('save_look/<int:look_id>/', save_look, name='save_look'),
    # path('regenerate_look/', regenerate_look, name='regenerate_look'),
    path('scrolling/', scrolling_page, name='scrolling'),
    path('like_look/', like_look, name='like_look'),
    path('dislike_look/', dislike_look, name='dislike_look'),
    path('user/<str:username>/', profile_page, name='profile'),
    path('get_city_by_coords/', get_city_by_coords, name='get_city_by_coords'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:  # Только для режима разработки (DEBUG=True)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)