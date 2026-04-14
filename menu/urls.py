from django.urls import path

from .views import MenuItemDetailView, MenuItemsApiView, MenuListView, health_check, menu_autocomplete

app_name = "menu"

urlpatterns = [
    path("", MenuListView.as_view(), name="list"),
    path("api/items/", MenuItemsApiView.as_view(), name="api-items"),
    path("api/health/", health_check, name="health"),
    path("item/<slug:slug>/", MenuItemDetailView.as_view(), name="detail"),
    path("api/autocomplete/", menu_autocomplete, name="autocomplete"),
]
