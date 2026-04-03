from django.urls import path

from .views import MenuItemDetailView, MenuItemsApiView, MenuListView

app_name = "menu"

urlpatterns = [
    path("", MenuListView.as_view(), name="list"),
    path("api/items/", MenuItemsApiView.as_view(), name="api-items"),
    path("item/<slug:slug>/", MenuItemDetailView.as_view(), name="detail"),
]
