from rest_framework import serializers
from .models import Ingredient, RecipeIngredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class IngredientReadSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        recipe = self.context.get('recipe')
        if recipe is None:
            return None
        recipe_ingredient = RecipeIngredient.objects.filter(
            recipe=recipe,
            ingredient=obj
        ).first()
        return recipe_ingredient.amount if recipe_ingredient else None
