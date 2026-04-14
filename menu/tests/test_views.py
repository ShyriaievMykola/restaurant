from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from menu.models import Category, MenuItem, Tag


class MenuListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        mains = Category.objects.create(name="Mains", slug="mains")
        pasta = Category.objects.create(name="Pasta", slug="pasta", parent=mains)
        desserts = Category.objects.create(name="Desserts", slug="desserts")

        vegan = Tag.objects.create(name="Vegan", slug="vegan")
        spicy = Tag.objects.create(name="Spicy", slug="spicy")

        cls.item_a = MenuItem.objects.create(
            name="Arrabbiata",
            slug="arrabbiata",
            description="Tomato pasta",
            price=Decimal("12.50"),
            is_available=True,
            category=pasta,
            popularity_score=13,
        )
        cls.item_a.tags.add(spicy)

        cls.item_b = MenuItem.objects.create(
            name="Garden Salad",
            slug="garden-salad",
            description="Greens and seeds",
            price=Decimal("9.00"),
            is_available=True,
            category=mains,
            popularity_score=30,
        )
        cls.item_b.tags.add(vegan)

        cls.item_c = MenuItem.objects.create(
            name="Cheesecake",
            slug="cheesecake",
            description="Classic cheesecake",
            price=Decimal("7.00"),
            is_available=False,
            category=desserts,
            popularity_score=40,
        )

        cls.item_d = MenuItem.objects.create(
            name="Fusion Bowl",
            slug="fusion-bowl",
            description="Vegan and spicy bowl",
            price=Decimal("10.50"),
            is_available=True,
            category=mains,
            popularity_score=25,
        )
        cls.item_d.tags.add(vegan, spicy)

    def test_menu_list_page_loads(self):
        response = self.client.get(reverse("menu:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Menu Items")

    def test_parent_category_filter_includes_child_items(self):
        response = self.client.get(reverse("menu:list"), {"category": "mains"})
        items = list(response.context["items"])

        self.assertIn(self.item_a, items)
        self.assertIn(self.item_b, items)
        self.assertNotIn(self.item_c, items)

    def test_text_search_filters_results(self):
        response = self.client.get(reverse("menu:list"), {"q": "cheese"})
        items = list(response.context["items"])

        self.assertEqual(items, [self.item_c])

    def test_tag_filter_returns_matching_items(self):
        response = self.client.get(reverse("menu:list"), {"tags": ["vegan"]})
        items = list(response.context["items"])

        self.assertEqual(items, [self.item_d, self.item_b])

    def test_tag_filter_and_mode_returns_items_with_all_tags(self):
        response = self.client.get(
            reverse("menu:list"),
            {"tags": ["vegan", "spicy"], "tag_mode": "and"},
        )
        items = list(response.context["items"])

        self.assertEqual(items, [self.item_d])

    def test_price_filter_applies_min_and_max(self):
        response = self.client.get(
            reverse("menu:list"),
            {"min_price": "8", "max_price": "10"},
        )
        items = list(response.context["items"])

        self.assertEqual(items, [self.item_b])

    def test_availability_filter_only_in_stock(self):
        response = self.client.get(reverse("menu:list"), {"availability": "in_stock"})
        items = list(response.context["items"])

        self.assertIn(self.item_a, items)
        self.assertIn(self.item_b, items)
        self.assertNotIn(self.item_c, items)

    def test_sort_by_price_desc(self):
        response = self.client.get(reverse("menu:list"), {"sort": "price_desc"})
        items = list(response.context["items"])

        self.assertEqual(items[0], self.item_a)
        self.assertEqual(items[-1], self.item_c)

    def test_sort_by_popular(self):
        response = self.client.get(reverse("menu:list"), {"sort": "popular"})
        items = list(response.context["items"])

        self.assertEqual(items[0], self.item_c)

    def test_quick_stats_present_in_context(self):
        response = self.client.get(reverse("menu:list"), {"availability": "in_stock"})
        stats = response.context["quick_stats"]

        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["in_stock"], 3)
        self.assertEqual(stats["unavailable"], 0)
        self.assertIsNotNone(stats["avg_price"])

    def test_active_filter_chips_are_present(self):
        response = self.client.get(
            reverse("menu:list"),
            {"q": "arr", "availability": "in_stock", "tags": ["spicy"]},
        )

        chips = response.context["active_filter_chips"]
        labels = [chip["label"] for chip in chips]
        self.assertIn("Search: arr", labels)
        self.assertIn("In stock", labels)
        self.assertIn("Tag: Spicy", labels)

    def test_list_view_paginates_results(self):
        category = Category.objects.get(slug="mains")
        for index in range(7):
            MenuItem.objects.create(
                name=f"Extra Item {index}",
                slug=f"extra-item-{index}",
                price=Decimal("5.00") + Decimal(index),
                category=category,
            )

        response = self.client.get(reverse("menu:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["items"]), 6)

    def test_api_returns_filtered_results(self):
        response = self.client.get(
            reverse("menu:api-items"),
            {"tags": ["vegan", "spicy"], "tag_mode": "and", "page_size": 10},
        )
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["pagination"]["total"], 1)
        self.assertEqual(payload["items"][0]["slug"], "fusion-bowl")
        self.assertEqual(payload["filters"]["tag_mode"], "and")

    def test_api_uses_default_page_size_for_invalid_value(self):
        response = self.client.get(reverse("menu:api-items"), {"page_size": "invalid"})
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["pagination"]["page_size"], 20)

    def test_api_clamps_page_size_to_maximum(self):
        response = self.client.get(reverse("menu:api-items"), {"page_size": "999"})
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["pagination"]["page_size"], 100)


class MenuItemDetailViewTests(TestCase):
    def test_detail_page_loads(self):
        category = Category.objects.create(name="Soups", slug="soups")
        item = MenuItem.objects.create(
            name="Tom Yum",
            slug="tom-yum",
            description="Thai soup",
            price=Decimal("10.00"),
            category=category,
        )

        response = self.client.get(reverse("menu:detail", kwargs={"slug": item.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tom Yum")


class MenuAutocompleteViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Soups", slug="soups")
        vegan = Tag.objects.create(name="Vegan", slug="vegan")
        spicy = Tag.objects.create(name="Spicy", slug="spicy")

        cls.item = MenuItem.objects.create(
            name="Tom Yum",
            slug="tom-yum",
            description="Thai spicy soup",
            price=Decimal("10.00"),
            category=category,
        )
        cls.item.tags.add(vegan, spicy)

        MenuItem.objects.create(
            name="Tomato Soup",
            slug="tomato-soup",
            description="Classic tomato soup",
            price=Decimal("8.50"),
            category=category,
        )

    def test_autocomplete_returns_empty_for_short_query(self):
        response = self.client.get(reverse("menu:autocomplete"), {"q": "t"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"suggestions": []})

    def test_autocomplete_returns_matching_item_with_url(self):
        response = self.client.get(reverse("menu:autocomplete"), {"q": "tom"})
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload["suggestions"]), 2)
        self.assertEqual(payload["suggestions"][0]["name"], "Tom Yum")
        self.assertEqual(payload["suggestions"][0]["category"], "Soups")
        self.assertEqual(
            payload["suggestions"][0]["url"],
            reverse("menu:detail", kwargs={"slug": "tom-yum"}),
        )

    def test_autocomplete_sorts_results_by_name(self):
        response = self.client.get(reverse("menu:autocomplete"), {"q": "tom"})
        suggestions = response.json()["suggestions"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["name"] for item in suggestions], ["Tom Yum", "Tomato Soup"])
