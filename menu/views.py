from django.core.paginator import Paginator
from django.db.models import Avg, Max, Min, Q
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView

from .models import Category, MenuItem, Tag
from .services.filters import apply_menu_filters


def get_menu_base_queryset():
    return MenuItem.objects.select_related("category", "category__parent").prefetch_related("tags")

def menu_autocomplete(request):
    query = request.GET.get("q", "").strip()
    suggestions = []

    if len(query) >= 2:
        items = (
            get_menu_base_queryset()
            .filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(category__name__icontains=query)
                | Q(tags__name__icontains=query)
            )
            .order_by("name")
            .distinct()[:10]
        )

        suggestions = [
            {
                "name": item.name,
                "category": item.category.name,
                "url": reverse("menu:detail", kwargs={"slug": item.slug}),
            }
            for item in items
        ]

    return JsonResponse({"suggestions": suggestions})


def health_check(request):
    return JsonResponse({"status": "ok"})


class MenuListView(ListView):
    model = MenuItem
    template_name = "menu/menu_list.html"
    context_object_name = "items"
    paginate_by = 6

    def get_queryset(self):
        return apply_menu_filters(get_menu_base_queryset(), self.request.GET)

    def _get_active_filters(self):
        return {
            "q": self.request.GET.get("q", ""),
            "category": self.request.GET.get("category", ""),
            "tags": self.request.GET.getlist("tags"),
            "tag_mode": self.request.GET.get("tag_mode", "or"),
            "min_price": self.request.GET.get("min_price", ""),
            "max_price": self.request.GET.get("max_price", ""),
            "availability": self.request.GET.get("availability", "all"),
            "sort": self.request.GET.get("sort", "name"),
        }

    def _query_without(self, key, value=None):
        params = self.request.GET.copy()
        if value is None:
            params.pop(key, None)
        else:
            existing_values = params.getlist(key)
            params.pop(key, None)
            for existing in existing_values:
                if existing != value:
                    params.appendlist(key, existing)
        params.pop("page", None)
        return params.urlencode()

    def _build_active_filter_chips(self, active_filters):
        chips = []
        base_url = reverse("menu:list")
        category_name = ""
        if active_filters["category"]:
            category = Category.objects.filter(slug=active_filters["category"]).first()
            category_name = category.name if category else active_filters["category"]

        tag_names = {tag.slug: tag.name for tag in Tag.objects.filter(slug__in=active_filters["tags"])}

        if active_filters["q"]:
            query = self._query_without("q")
            chips.append({"label": f"Search: {active_filters['q']}", "remove_url": f"{base_url}?{query}" if query else base_url})

        if active_filters["category"]:
            query = self._query_without("category")
            chips.append({"label": f"Category: {category_name}", "remove_url": f"{base_url}?{query}" if query else base_url})

        for slug in active_filters["tags"]:
            query = self._query_without("tags", slug)
            chips.append({"label": f"Tag: {tag_names.get(slug, slug)}", "remove_url": f"{base_url}?{query}" if query else base_url})

        if active_filters["tag_mode"] == "and" and len(active_filters["tags"]) > 1:
            query = self._query_without("tag_mode")
            chips.append({"label": "Tags: match all", "remove_url": f"{base_url}?{query}" if query else base_url})

        if active_filters["min_price"]:
            query = self._query_without("min_price")
            chips.append({"label": f"Min: ${active_filters['min_price']}", "remove_url": f"{base_url}?{query}" if query else base_url})

        if active_filters["max_price"]:
            query = self._query_without("max_price")
            chips.append({"label": f"Max: ${active_filters['max_price']}", "remove_url": f"{base_url}?{query}" if query else base_url})

        if active_filters["availability"] == "in_stock":
            query = self._query_without("availability")
            chips.append({"label": "In stock", "remove_url": f"{base_url}?{query}" if query else base_url})

        if active_filters["sort"] != "name":
            query = self._query_without("sort")
            chips.append({"label": f"Sort: {active_filters['sort']}", "remove_url": f"{base_url}?{query}" if query else base_url})

        return chips

    def _build_quick_stats(self, queryset):
        total = queryset.count()
        in_stock = queryset.filter(is_available=True).count()
        unavailable = total - in_stock
        avg_price = queryset.aggregate(avg_price=Avg("price"))["avg_price"]
        return {
            "total": total,
            "in_stock": in_stock,
            "unavailable": unavailable,
            "avg_price": avg_price,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_filters = self._get_active_filters()

        price_limits = MenuItem.objects.aggregate(
            min_p=Min('price'), 
            max_p=Max('price')
        )

        context["min_limit"] = float(price_limits['min_p'] or 0)
        context["max_limit"] = float(price_limits['max_p'] or 100)
        context["top_categories"] = Category.objects.filter(parent__isnull=True).prefetch_related("children")
        context["tags"] = Tag.objects.all()
        context["active_filters"] = active_filters
        context["active_filter_chips"] = self._build_active_filter_chips(active_filters)
        context["quick_stats"] = self._build_quick_stats(self.get_queryset())
    
        params_without_page = self.request.GET.copy()
        params_without_page.pop("page", None)
        context["query_string_without_page"] = params_without_page.urlencode()
        return context


class MenuItemsApiView(View):
    def get(self, request, *args, **kwargs):
        queryset = apply_menu_filters(get_menu_base_queryset(), request.GET)

        page_number = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 20)
        try:
            page_size = max(1, min(int(page_size), 100))
        except (TypeError, ValueError):
            page_size = 20

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page_number)

        items = [
            {
                "id": item.id,
                "name": item.name,
                "slug": item.slug,
                "description": item.description,
                "price": str(item.price),
                "is_available": item.is_available,
                "category": item.category.name,
                "category_slug": item.category.slug,
                "tags": [tag.name for tag in item.tags.all()],
                "popularity_score": item.popularity_score,
            }
            for item in page_obj.object_list
        ]

        stats = {
            "total": queryset.count(),
            "in_stock": queryset.filter(is_available=True).count(),
            "avg_price": queryset.aggregate(avg_price=Avg("price"))["avg_price"],
        }

        if stats["avg_price"] is not None:
            stats["avg_price"] = str(stats["avg_price"])

        return JsonResponse(
            {
                "items": items,
                "pagination": {
                    "page": page_obj.number,
                    "page_size": page_size,
                    "num_pages": paginator.num_pages,
                    "total": paginator.count,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous(),
                },
                "stats": stats,
                "filters": {
                    "q": request.GET.get("q", ""),
                    "category": request.GET.get("category", ""),
                    "tags": request.GET.getlist("tags"),
                    "tag_mode": request.GET.get("tag_mode", "or"),
                    "min_price": request.GET.get("min_price", ""),
                    "max_price": request.GET.get("max_price", ""),
                    "availability": request.GET.get("availability", "all"),
                    "sort": request.GET.get("sort", "name"),
                },
            }
        )


class MenuItemDetailView(DetailView):
    model = MenuItem
    template_name = "menu/item_detail.html"
    context_object_name = "item"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return get_menu_base_queryset()


