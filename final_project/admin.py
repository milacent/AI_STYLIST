from django.contrib import admin
from .models import ClothingItem

@admin.register(ClothingItem)
class ClothingItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'image_name', 'min_temp', 'max_temp')
    list_filter = ('category',)
    search_fields = ('name', 'category')