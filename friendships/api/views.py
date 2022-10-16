from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    #FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User


class FriendshipViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()

    # url looks like
    # get the follower of 1
    # /api/friendships/1/followers/
    @action(methods=["GET"], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response({
            'followers': serializer.data,
        },
            status=status.HTTP_200_OK,
        )

    @action(methods=["GET"], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)
        return Response({
            'following': serializer.data,
        },
            status=status.HTTP_200_OK,
        )
    # we can rewrite list to implement followings and followers
    def list(self, request):
        return Response({'message': 'This is friendships homepage'})

