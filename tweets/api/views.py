from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer#,  TweetCreateSerializer
from tweets.models import Tweet

# 尽量少用ModelViewSet 因为不是每个人都有增删查改的权限
class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    queryset = Tweet.objects.all()
    #serializer_class = TweetCreateSerializer
    serializer_class = TweetSerializer


    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        return [IsAuthenticated()]


    def list(self, request):
        if "user_id" not in request.query_params:
            return Response('Missing user_id', status=400)

        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')

        serializer = TweetSerializer(tweets,many=True)
        return Response({'tweet':serializer.data})

    def create(self, request, *args, **kwargs):
        pass

