from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import pagination, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ads.models import Ad, Comment
from ads.permissions import AdAdminPermission, IsExecutor
from ads.serializers import AdSerializer, CommentSerializer
from ads.filters import AdFilter


class Logout(APIView):
    """ ВЫХОД ИЗ АККАУНТА И УДАЛЕНИЕ Token АВТОРИЗАЦИИ """
    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class AdPagination(pagination.PageNumberPagination):
    """ Пагинация на страницу не более 4 объектов """
    page_size = 4


class AdViewSet(viewsets.ModelViewSet):
    """ Вьюсет который выводит список всех объектов """
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    pagination_class = AdPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AdFilter
    # http_method_names = ["patch", "get", "post", "delete"]
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action == "retrieve":
            self.permission_classes = [IsAuthenticated, ]
        elif self.action in ["create", "update", "partial_update", "destroy", "me"]:
            self.permission_classes = [IsAuthenticated, AdAdminPermission | IsExecutor]

        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request, *args, **kwargs):
        self.queryset = Ad.objects.filter(author=request.user)
        return super().list(self, request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def perform_update(self, serializer):
    #     serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ Вьюсет который выводит список всех объектов """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = None
    # http_method_names = ["patch", "get", "post", "delete"]

    def perform_create(self, serializer):
        ads_id = self.kwargs.get("ads_pk")
        ad_instance = get_object_or_404(Ad, id=ads_id)
        user = self.request.user
        serializer.save(author=user, ad=ad_instance)

    def get_queryset(self, *args, **kwargs):
        comment = self.kwargs.get('ads_pk')
        return super().get_queryset().filter(ad=comment)

    def get_permissions(self):
        if self.action == "retrieve":
            self.permission_classes = [IsAuthenticated, ]
        elif self.action in ["create", "update", "partial_update", "destroy", ]:
            self.permission_classes = [IsAuthenticated, AdAdminPermission | IsExecutor]
        return super().get_permissions()

    # ==== ПАМЯТКА === ВАРИАНТ КАК МОЖНО ВЫГРУЗИТЬ ВСЕ КОММЕНТАРИИ К ОБЪЯВЛЕНИЮ === ПАМЯТКА ==========
    # def get_queryset(self):
    #     ad_id = self.kwargs.get("ad_pk")
    #     ad_instance = get_object_or_404(Ad, id=ad_id)
    #     return ad_instance.comments.all()

    # def get_permissions(self):
    #     permission_classes = (IsAuthenticated,)
    #     if self.action in ["list", "retrieve"]:
    #         permission_classes = (IsAuthenticated,)
    #     elif self.action in ["create", "update", "partial_update", "destroy"]:
    #         permission_classes = (IsOwner | IsAdmin,)
    #     return tuple(permission() for permission in permission_classes)
