from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (TweetSerializer, \
                                    TweetSerializerForCreate, \
                                    TweetSerializerForDetails,)
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService
from utils.paginations import EndlessPagination
from tweets.services import TweetService
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit


# 尽量少用ModelViewSet 因为不是每个人都有增删查改的权限
class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate
    pagination_class = EndlessPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        return Response(TweetSerializerForDetails(tweet, context={'request': request}).data)

    @method_decorator(ratelimit(key='user', rate='1/s', method='POST', block=True))
    @method_decorator(ratelimit(key='user', rate='5/m', method='POST', block=True))
    def list(self, request):
        if "user_id" not in request.query_params:
            return Response('Missing user_id', status=400)

        # here if you visit localhost:8000/api/tweets/?user_id = 1
        # it shows you the tweets user#1 made and they are ordered by
        # "-created_at"
        # tweets = Tweet.objects.filter(
        #     user_id=request.query_params['user_id']
        # ).order_by('-created_at')
        user_id = request.query_params["user_id"]
        tweets = TweetService.get_cached_tweet(user_id=user_id)
        page = self.paginator.paginate_cached_list(tweets, request)

        if page is None:
            tweets = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
            page = self.paginate_queryset(tweets)

        serializer = TweetSerializer(page, context={'request': request}, many=True)
        return self.get_paginated_response(data=serializer.data)

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
        return Response(TweetSerializer(
            tweet,
            context={'request': request},
        ).data, status=201)

