from django.contrib import admin
from django.contrib.admin import display
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            Shopping_cart, Tag)
from users.models import Subscriptions


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'colour', 'slug')
    # list_editable = ('colour', 'name')
    search_fields = ('name', 'colour')
    # list_filter = ('slug',)
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagAdmin)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    # list_editable = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'id', 'cooking_time', 'count_favorites')
    # list_editable = ('ingredients', 'cooking_time', 'name')
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    # inlines = (IngredientRecipeInLine)
    # readonly_fields = ('added_in_favorites',)
    empty_value_display = '-пусто-'

    @display(description='в избранных')
    def count_favorites(self, obj):
        return obj.in_favorites.count()


admin.site.register(Recipe, RecipeAdmin)


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    # list_editable = ('Recipe', 'Amount')
    search_fields = ('ingredient',)
    list_filter = ('recipe',)
    empty_value_display = '-пусто-'


admin.site.register(IngredientRecipe, IngredientRecipeAdmin)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'date_added')
    # list_editable = ('recipe')
    search_fields = ('recipe',)
    # list_filter = ('user',)
    empty_value_display = '-пусто-'


admin.site.register(Favorite, FavoriteAdmin)


class Shopping_CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'date_added')
    # list_editable = ('recipe')
    search_fields = ('recipe', 'user')
    # list_filter = ('user',)
    empty_value_display = '-пусто-'


admin.site.register(Shopping_cart, Shopping_CartAdmin)


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    # list_editable = ('User')
    # search_fields = ('user')
    # list_filter = ('user')
    empty_value_display = '-пусто-'


admin.site.register(Subscriptions, SubscriptionsAdmin)
