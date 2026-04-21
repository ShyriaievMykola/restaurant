from django.contrib import admin

from .models import Category, MenuItem, Order, OrderItem, Tag


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
	search_fields = ("name", "slug", "description", "category__name")
	prepopulated_fields = {"slug": ("name",)}
	filter_horizontal = ("tags",)
	list_select_related = ("category",)
	list_per_page = 50
	ordering = ("name",)


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0
	fields = ("menu_item", "price", "quantity", "total_price")
	readonly_fields = ("total_price",)
	autocomplete_fields = ("menu_item",)

	def total_price(self, obj):
		if not obj.pk:
			return "-"
		return obj.total_price


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = (
		"order_uuid",
		"first_name",
		"last_name",
		"email",
		"phone",
		"status",
		"total_quantity",
		"total_price",
		"created_at",
	)
	list_filter = ("status", "created_at", "updated_at")
	search_fields = (
		"order_uuid",
		"first_name",
		"last_name",
		"email",
		"phone",
	)
	readonly_fields = ("order_uuid", "created_at", "updated_at", "total_quantity", "total_price")
	date_hierarchy = "created_at"
	ordering = ("-created_at",)
	inlines = (OrderItemInline,)
	list_per_page = 50


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
	list_display = ("id", "order", "menu_item", "price", "quantity", "total_price")
	list_filter = ("order__status", "menu_item")
	search_fields = ("order__order_uuid", "menu_item__name")
	list_select_related = ("order", "menu_item")
	autocomplete_fields = ("order", "menu_item")

