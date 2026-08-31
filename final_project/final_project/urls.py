from django.contrib import admin
from django.urls import path, include
from final_project_app.views import *
from django.conf import settings
from django.conf.urls.static import static

handler404 = Handle400

urlpatterns = [
    path('', include('django_prometheus.urls')),
    path('admin/', admin.site.urls),
    path('', index_page, name='index'),
    path('log_in/', log_in_page, name='log_in'),
    path('sign_up/', sign_up_page, name='sign_up'),
    path('profile/saved/', view_all_saved, name='view_all_saved'),
    path('profile/liked/', view_all_liked, name='view_all_liked'),
    path('profile/disliked/', view_all_disliked, name='view_all_disliked'),
    path('profile/', profile_redirect, name='profile_redirect'),
    path('profile/<str:username>/', profile_page, name='profile'),
    path('profile_edit/', profile_edit_page, name='profile_edit'),
    path('gallery_liked/', gallery_liked_page, name='gallery_liked'),
    path('scrolling/', scrolling_page, name='scrolling'),
    path('about/', about_page, name='about'),
    path('terms/', terms_page, name='terms'),
    path('get_city_by_coords/', get_city_by_coords, name='get_city_by_coords'),
    path('for_you/', for_you_page, name='for_you_default'),
    path('for_you/<str:city>/', for_you_page, name='for_you'),
    path('log_out/', log_out, name='log_out'),
    path('post/', post_page, name='post'),
    path('post/<int:id>', post_page, name='post'),
    path('send_like_post/<int:id>', send_like_post, name='like'),
    # path('item/', item_page, name='items'),
    # path('item/<int:id>', item_page, name='item'),
    path('catalog/', catalog_page, name='catalog'),
    path('posts_all/', post_list, name='posts_all'),
    path('save_look/', save_look_empty, name='save_look_empty'),
    path('make/', make_post_page, name='make_post'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:  # Только для режима разработки (DEBUG=True)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
