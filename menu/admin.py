from django.contrib import admin

from .models import Category, MenuItem, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("name", "parent")
	list_filter = ("parent",)
	search_fields = ("name", "slug")
	prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	list_display = ("name",)
	search_fields = ("name", "slug")
	prepopulated_fields = {"slug": ("name",)}


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
	list_display = ("name", "category", "price", "is_available", "popularity_score", "updated_at")
	list_filter = ("category", "is_available", "tags")
	search_fields = ("name", "slug", "description")
	prepopulated_fields = {"slug": ("name",)}
	filter_horizontal = ("tags",)
	list_select_related = ("category",)
