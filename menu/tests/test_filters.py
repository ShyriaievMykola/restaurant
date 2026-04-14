from decimal import Decimal

from django.http import QueryDict
from django.test import TestCase

from menu.models import Category, MenuItem, Tag
from menu.services.filters import _safe_decimal, apply_menu_filters


class SafeDecimalTests(TestCase):
    def test_safe_decimal_returns_none_for_invalid_value(self):
        self.assertIsNone(_safe_decimal("abc"))

    def test_safe_decimal_parses_valid_value(self):
        self.assertEqual(_safe_decimal("10.25"), Decimal("10.25"))


class ApplyMenuFiltersTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        mains = Category.objects.create(name="Mains", slug="mains")
        vegan = Tag.objects.create(name="Vegan", slug="vegan")

        cls.item_a = MenuItem.objects.create(
            name="Alpha",
            slug="alpha",
            description="First",
            price=Decimal("10.00"),
            is_available=True,
            category=mains,
            popularity_score=1,
        )
        cls.item_a.tags.add(vegan)

        cls.item_b = MenuItem.objects.create(
            name="Beta",
            slug="beta",
            description="Second",
            price=Decimal("20.00"),
            is_available=False,
            category=mains,
            popularity_score=2,
        )

    def test_invalid_min_price_is_ignored(self):
        params = QueryDict("min_price=not-a-number")
        queryset = apply_menu_filters(MenuItem.objects.all(), params)

        self.assertEqual(list(queryset), [self.item_a, self.item_b])

    def test_availability_filter_returns_only_in_stock(self):
        params = QueryDict("availability=in_stock")
        queryset = apply_menu_filters(MenuItem.objects.all(), params)

        self.assertEqual(list(queryset), [self.item_a])