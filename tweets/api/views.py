from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService


# 尽量少用ModelViewSet 因为不是每个人都有增删查改的权限
class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate
    #serializer_class = TweetSerializer

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        if "user_id" not in request.query_params:
            return Response('Missing user_id', status=400)

        # here if you visit localhost:8000/api/tweets/?user_id = 1
        # it shows you the tweets user#1 made and they are ordered by
        # "-created_at"
        tweets = Tweet.objects.filter(
    
            user_id=request.query_params['user_id']
        ).order_by('-created_at')

        serializer = TweetSerializer(tweets,many=True)
        return Response({'tweet':serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=400)

        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet).data, status=201)

