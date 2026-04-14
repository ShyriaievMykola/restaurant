from django.urls import path

from .views import (
    MenuItemDetailView,
    MenuItemsApiView,
    MenuListView,
    cart_detail,
    checkout,
    add_to_cart,
    remove_from_cart,
    order_success,
    health_check,
    menu_autocomplete,
)

app_name = "menu"

urlpatterns = [
    path("", MenuListView.as_view(), name="list"),
    path("cart/", cart_detail, name="cart"),
    path("cart/add/<slug:slug>/", add_to_cart, name="cart-add"),
    path("cart/remove/<slug:slug>/", remove_from_cart, name="cart-remove"),
    path("checkout/", checkout, name="checkout"),
    path("order/success/<uuid:order_uuid>/", order_success, name="order-success"),
    path("api/items/", MenuItemsApiView.as_view(), name="api-items"),
    path("api/health/", health_check, name="health"),
    path("item/<slug:slug>/", MenuItemDetailView.as_view(), name="detail"),
    path("api/autocomplete/", menu_autocomplete, name="autocomplete"),
]
