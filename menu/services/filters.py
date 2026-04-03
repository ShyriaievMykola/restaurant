from decimal import Decimal, InvalidOperation

from django.db.models import Count, Q


def _safe_decimal(value):
    if value in (None, ""):
        return None
    try:
        return Decimal(value)
    except (TypeError, InvalidOperation):
        return None


def apply_menu_filters(queryset, params):
    search_query = params.get("q", "").strip()
    category_slug = params.get("category", "").strip()
    tag_slugs = [slug for slug in params.getlist("tags") if slug]
    tag_mode = params.get("tag_mode", "or").lower()
    min_price = _safe_decimal(params.get("min_price"))
    max_price = _safe_decimal(params.get("max_price"))
    availability = params.get("availability", "all")
    sort = params.get("sort", "name")

    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(tags__name__icontains=search_query)
        )

    if category_slug:
        queryset = queryset.filter(
            Q(category__slug=category_slug) | Q(category__parent__slug=category_slug)
        )

    if tag_slugs:
        if tag_mode == "and":
            queryset = queryset.filter(tags__slug__in=tag_slugs).annotate(
                matched_tags=Count("tags", filter=Q(tags__slug__in=tag_slugs), distinct=True)
            ).filter(matched_tags=len(tag_slugs))
        else:
            queryset = queryset.filter(tags__slug__in=tag_slugs)

    if min_price is not None:
        queryset = queryset.filter(price__gte=min_price)

    if max_price is not None:
        queryset = queryset.filter(price__lte=max_price)

    if availability == "in_stock":
        queryset = queryset.filter(is_available=True)

    ordering = {
        "price_asc": ["price", "name"],
        "price_desc": ["-price", "name"],
        "popular": ["-popularity_score", "name"],
        "newest": ["-created_at", "-id"],
        "name": ["name"],
    }

    queryset = queryset.order_by(*ordering.get(sort, ordering["name"]))

    if search_query or tag_slugs:
        queryset = queryset.distinct()

    return queryset
