from collections import defaultdict

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.pagination import LimitPageNumberPagination

from .filters import RecipeFilter
from .models import Recipe, ShoppingCart
from .serializers import (
    RecipeCreateSerializer,
    RecipeReadSerializer,
    RecipeShortSerializer
)
from .permissions import IsAuthorOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user

        is_in_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_cart in ['1', 'true', 'True'] and user.is_authenticated:
            queryset = queryset.filter(in_shopping_carts__user=user)

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited in ['1', 'true', 'True'] and user.is_authenticated:
            queryset = queryset.filter(favorites__user=user)

        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Необходимо авторизоваться для создания рецепта.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        read_serializer = RecipeReadSerializer(
            recipe, context={'request': request}
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        short_code = f"s/{recipe.id}"
        domain = "https://foodgram.example.org"
        short_link = f"{domain}/{short_code}"

        return Response({"short-link": short_link}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"detail": "Рецепт уже в корзине."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            cart_item = ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).first()
            if not cart_item:
                return Response(
                    {"detail": "Рецепта нет в корзине."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user
        cart_items = user.shopping_cart.select_related('recipe').all()

        ingredients = defaultdict(lambda: {'amount': 0, 'unit': ''})

        for item in cart_items:
            for ri in item.recipe.recipeingredient_set.all():
                ing = ri.ingredient
                key = (ing.name, ing.measurement_unit)
                ingredients[key]['amount'] += ri.amount
                ingredients[key]['unit'] = ing.measurement_unit

        lines = ["Список покупок:\n\n"]
        for (name, unit), data in ingredients.items():
            lines.append(f"▪ {name} — {data['amount']} {unit}\n")

        response = HttpResponse(
            "".join(lines),
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment;',
            'filename="shopping_list.txt"'
        )
        return response

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if recipe.favorites.filter(user=user).exists():
                return Response(
                    {"detail": "Рецепт уже в избранном."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe.favorites.create(user=user)
            data = {
                "id": recipe.id,
                "name": recipe.name,
                "image": request.build_absolute_uri(recipe.image.url),
                "cooking_time": recipe.cooking_time,
            }
            return Response(data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favorite = recipe.favorites.filter(user=user).first()
            if not favorite:
                return Response(
                    {"detail": "Рецепта нет в избранном."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
