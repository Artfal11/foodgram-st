from rest_framework import viewsets, permissions

from ingredients.models import Ingredient
from .serializers import IngredientSerializer
from .filters import IngredientNameFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientNameFilter]
    permission_classes = [permissions.AllowAny]
    pagination_class = None
