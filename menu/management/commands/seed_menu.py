from decimal import Decimal

from django.core.management.base import BaseCommand

from menu.models import Category, MenuItem, Tag


class Command(BaseCommand):
    help = "Create demo categories, tags, and menu items for local development"

    def handle(self, *args, **options):
        categories = {
            "mains": self._category("Mains", "mains"),
            "pasta": self._category("Pasta", "pasta", parent_slug="mains"),
            "grill": self._category("Grill", "grill", parent_slug="mains"),
            "desserts": self._category("Desserts", "desserts"),
            "drinks": self._category("Drinks", "drinks"),
            "coffee": self._category("Coffee", "coffee", parent_slug="drinks"),
        }

        tags = {
            "vegan": self._tag("Vegan", "vegan"),
            "spicy": self._tag("Spicy", "spicy"),
            "gluten_free": self._tag("Gluten Free", "gluten-free"),
            "signature": self._tag("Signature", "signature"),
        }

        items_data = [
            ("Arrabbiata", "arrabbiata", "Tomato sauce, chili, garlic", "pasta", "12.50", True, 81, ["spicy", "signature"]),
            ("Garden Salad", "garden-salad", "Leafy greens, avocado, seeds", "mains", "9.20", True, 57, ["vegan", "gluten_free"]),
            ("Lemon Chicken", "lemon-chicken", "Chargrilled chicken with herbs", "grill", "14.90", True, 63, ["signature"]),
            ("Mushroom Risotto", "mushroom-risotto", "Creamy arborio rice and mushrooms", "mains", "13.40", True, 44, []),
            ("Cheesecake", "cheesecake", "Vanilla cheesecake with berries", "desserts", "7.40", True, 72, []),
            ("Dark Brownie", "dark-brownie", "Chocolate brownie with walnut", "desserts", "6.80", False, 38, []),
            ("Flat White", "flat-white", "Espresso with silky microfoam", "coffee", "4.50", True, 69, ["signature"]),
            ("Cold Brew", "cold-brew", "Slow steeped arabica coffee", "coffee", "4.20", True, 33, ["gluten_free"]),
            ("Ginger Lemonade", "ginger-lemonade", "Fresh lemon and ginger soda", "drinks", "3.90", True, 50, ["vegan", "gluten_free"]),
            ("Spicy Tofu Bowl", "spicy-tofu-bowl", "Tofu, rice, pickled vegetables", "mains", "11.80", True, 41, ["vegan", "spicy"]),
            ("Sea Bass", "sea-bass", "Pan-seared sea bass with greens", "grill", "16.70", True, 59, ["gluten_free"]),
            ("Panna Cotta", "panna-cotta", "Cream dessert with fruit coulis", "desserts", "6.90", True, 36, []),
        ]

        created_count = 0
        updated_count = 0
        for name, slug, description, category_key, price, is_available, popularity, item_tags in items_data:
            item, created = MenuItem.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": description,
                    "category": categories[category_key],
                    "price": Decimal(price),
                    "is_available": is_available,
                    "popularity_score": popularity,
                },
            )
            item.tags.set([tags[tag_slug] for tag_slug in item_tags])
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS("Menu seed complete"))
        self.stdout.write(f"Created items: {created_count}")
        self.stdout.write(f"Updated items: {updated_count}")

    def _category(self, name, slug, parent_slug=None):
        parent = None
        if parent_slug:
            parent = Category.objects.get(slug=parent_slug)
        category, _ = Category.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "parent": parent},
        )
        category.name = name
        category.parent = parent
        category.save()
        return category

    def _tag(self, name, slug):
        tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
        tag.name = name
        tag.save()
        return tag
