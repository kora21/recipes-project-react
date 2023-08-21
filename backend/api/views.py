from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponse
from djoser.views import UserViewSet
# from rest_framework.decorators import api_view
from rest_framework import permissions
from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.routers import APIRootView
from rest_framework.status import (HTTP_201_CREATED, HTTP_400_BAD_REQUEST,
                                   HTTP_204_NO_CONTENT)
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from django.db.models import Sum
from rest_framework import viewsets
from recipes.models import (Favorite, Ingredient, IngredientRecipe,
                            Recipe, Shopping_cart, Subscriptions, Tag)
from api.filters import IngredientFilter, RecipeFilter
from api.paginator import CustomPagination
from api.permissions import (IsAdminOrReadOnly, IsOwnerOrReadOnly, )
from api.serializers import (IngredientSerializer,
                             RecipeCreateSerializer,
                             RecipeReadSerializer,
                             RecipeShortSerializer,
                             CustomUserSerializer,
                             CustomUserCreateSerializer,
                             UserSubscribeSerializer,
                             TagSerializer)


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Работает с пользователями."""
    queryset = User.objects.all()
    # permission_classes = (IsAuthenticated,)
    # serializer_class = CustomUserSerializer
    # serializer_class = UserSubscribeSerializer
    pagination_class = CustomPagination
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(detail=True, permission_classes=(IsAuthenticated,),
            methods=['post', 'delete'],)
    def subscribe(self, request, **kwargs):
        """Создаёт/удалет связь между пользователями."""
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            serializer = UserSubscribeSerializer(author,
                                                 data=request.data,
                                                 context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscriptions.objects.create(user=user, author=author)
            return Response(serializer.data, status=HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(Subscriptions,
                                             user=user,
                                             author=author)
            subscription.delete()
            return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Список подписок пользоваетеля."""
        pages = self.paginate_queryset(
            User.objects.filter(subscriber__user=self.request.user)
        )
        serializer = UserSubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Работает с тэгами.Изменение и создание тэгов разрешено только
    админам."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly, )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Работет с ингридиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)


class RecipeViewSet(viewsets.ModelViewSet):
    """Работает с рецептами. Изменять рецепт может только автор или админы.
    Для авторизованных пользователей возможность добавить рецепт в избранное
    и в список покупок. Скачать текстовый файл со списком покупок"""
    queryset = Recipe.objects.all()
    # permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    
    def get_serializer_class(self):
        """Переопределение сериалайзера в зависимости от запроса"""
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer
    
    def perform_create(self, serializer):
        """Добавление автора рецепта"""
        serializer.save(author=self.request.user)

    # def get_permissions(self):
    #     if self.action == 'update' or self.action == 'destroy':
    #         return (IsOwnerOrReadOnly,)
    #     return super().get_permissions()

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        """Добавление рецепта в список покупок"""
        if request.method == 'POST':
            return self.add_to(Shopping_cart, request.user, pk)
        return self.delete_from(Shopping_cart, request.user, pk)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        """Добавление рецепта в избранное"""
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        return self.delete_from(Favorite, request.user, pk)

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=HTTP_400_BAD_REQUEST)

    @action(methods=("get",), detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Загружает файл *.txt со списком покупок."""
        user = request.user
        if not user.in_shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients = IngredientRecipe.objects.filter(
            recipe__in_shopping_cart__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_list = ['Список Покупок:']
        for ingredient in ingredients:
            shopping_list.append(
                f"{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f" - {ingredient['amount']}"
            )
        shopping_list = '\n'.join(shopping_list)
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response

