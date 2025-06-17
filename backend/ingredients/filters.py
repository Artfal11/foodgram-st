from rest_framework import filters


class IngredientNameFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        name_param = request.query_params.get('name')
        if name_param:
            return queryset.filter(name__istartswith=name_param)
        return queryset
