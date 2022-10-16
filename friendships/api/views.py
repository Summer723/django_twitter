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


class FriendshipViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = FriendshipSerializerForCreate

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
            'followings': serializer.data,
        },
            status=status.HTTP_200_OK,
        )

    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
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
        return Response(
            FollowingSerializer(instance).data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        unfollow_user= self.get_object()
        if request.user.id == unfollow_user.id:
            return Response(
                {
                  'success': False,
                  'message': "You cannot unfollow yourself",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
            return Response({
                'success': False,
                'message': "You do not follow this user"
            },
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted, _ = Friendship.objects.filter(
            from_user=request.user.id,
            to_user=unfollow_user,
        ).delete()
        return Response({"success": True, 'deleted': deleted})



    # we can rewrite list to implement followings and followers
    def list(self, request):
        return Response({'message': 'This is friendships homepage'})

