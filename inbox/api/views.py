from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from inbox.api.serializers import (
    NotificationSerializer,
    NotificationSerializerForUpdate,
)
from rest_framework import viewsets, status
from notifications.models import Notification
from utils.decorators import required_params
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit


class NotificationViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
):

    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('unread',)

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(methods=["GET"], detail=False, url_path='unread-count')
    @method_decorator(ratelimit(key='user', rate='3/s', method='GET', block=True))
    def unread_count(self, request, *args, **kwargs):
        count = self.get_queryset().filter(unread=True).count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path='mark-all-as-read')
    @method_decorator(ratelimit(key='user', rate='3/s', method='POST', block=True))
    def mark_all_as_read(self, request, *args, **kwargs):
        updated = self.get_queryset().filter(unread=True).update(unread=False)
        return Response({'marked_count': updated}, status=status.HTTP_200_OK)

    @required_params(method='POST', params=['unread'])
    @method_decorator(ratelimit(key='user', rate='3/s', method='POST', block=True))
    def update(self, request, *args, **kwargs):
        serializer = NotificationSerializerForUpdate(
            instance=self.get_object(),
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'message': "Please check your input",
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        notification = serializer.save()
        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK,
        )




