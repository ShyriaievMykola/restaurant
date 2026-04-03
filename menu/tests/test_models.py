from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from menu.models import Category, MenuItem, Tag


class CategoryModelTests(TestCase):
    def test_cannot_create_third_level_category(self):
        root = Category.objects.create(name="Food", slug="food")
        child = Category.objects.create(name="Pasta", slug="pasta", parent=root)

        with self.assertRaises(ValidationError):
            Category.objects.create(name="Ravioli", slug="ravioli", parent=child)

    def test_unique_name_per_same_parent(self):
        root = Category.objects.create(name="Drinks", slug="drinks")
        Category.objects.create(name="Coffee", slug="coffee", parent=root)

        with self.assertRaises(ValidationError):
            Category.objects.create(name="Coffee", slug="coffee-2", parent=root)


class MenuItemModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Main", slug="main")

    def test_menu_item_price_must_be_positive(self):
        with self.assertRaises(ValidationError):
            MenuItem.objects.create(
                name="Broken Dish",
                slug="broken-dish",
                price=Decimal("0.00"),
                category=self.category,
            )

    def test_tag_slug_must_be_unique(self):
        Tag.objects.create(name="Vegan", slug="vegan")

        with self.assertRaises(ValidationError):
            Tag.objects.create(name="Plant Based", slug="vegan")
