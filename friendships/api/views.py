from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User
from utils.paginations import MyPagination
from friendships.services import FriendshipService
from ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator


class FriendshipViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = FriendshipSerializerForCreate
    pagination_class = MyPagination

    # url looks like
    # get the follower of 1
    # /api/friendships/1/followers/
    @action(methods=["GET"], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key="user_or_ip", method="GET", rate="3/s", block=True))
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowerSerializer(page, many=True, context={'request':request})
        return self.get_paginated_response(serializer.data)

    @action(methods=["GET"], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key="user_or_ip", method="GET", rate="3/s", block=True))
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowingSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key="user", method="POST", rate="10/s", block=True))
    def follow(self, request, pk):
        # if you want to check whether the user I am trying to follow exists
        # self.get_object() will try to find object using "pk"
        self.get_object()

        # if Friendship.objects.filter(from_user=request.user,to_user=pk).exists():
        #     return Response({
        #         'success': True,
        #         'duplicates': True,
        #     },
        #         status=status.HTTP_201_CREATED,
        #     )
        serializer = FriendshipSerializerForCreate(
            data=
            {
                'from_user_id':request.user.id,
                'to_user_id':pk,
            },
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                "errors": serializer.errors,
            },
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        FriendshipService.invalidate_following_cache(request.user.id)

        return Response(
            FollowingSerializer(instance, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key="user", method="POST", rate="10/s", block=True))
    def unfollow(self, request, pk):
        unfollow_user = self.get_object()
        if request.user.id == unfollow_user.id:
            return Response(
                {
                  'success': False,
                  'message': "You cannot unfollow yourself",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        FriendshipService.invalidate_following_cache(request.user.id)
        deleted, _ = Friendship.objects.filter(
            from_user=request.user.id,
            to_user=unfollow_user,
        ).delete()
        return Response({"success": True, 'deleted': deleted})

    # we can rewrite list to implement followings and followers
    def list(self, request):
        return Response({'message': 'This is friendships homepage'})

