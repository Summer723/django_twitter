from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.models import UserProfile
from accounts.api.serializers import (
    UserSerializer,
    LoginSerializer,
    SignupSerializer,
    UserProfileSerializerForUpdate,
    UserSerializerWithProfile,
)
from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
    authenticate as django_authenticate,
     )
from utils.permissions import IsObjectOwner
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializerWithProfile
    permission_classes = [permissions.IsAdminUser]


class AccountViewSet(viewsets.ViewSet):

    # serializer_class = LoginSerializer
    serializer_class = SignupSerializer
    # if you want to define some functionality on the object then detail = true

    @action(methods=['GET'], detail=False)
    @method_decorator(ratelimit(key='user', rate='3/s', method='GET', block=True))
    def login_status(self, request):
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data

        return Response(data)

    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key='ip', rate='3/s', method='POST', block=True))
    def logout(self, request):
        django_logout(request)
        return Response({"Success": True})

    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key="ip", rate="3/s", method="POST", block=True))
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors
            }, status=400)
            # 400 stands for bad request # 200 is good
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        if not User.objects.filter(username=username).exists():
            return Response({
                'success': False,
                'message': "User does not exist."
            }, status=400)

        # it is valid, try to login
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                'success': False,
                'message': "Username and password do not match"
            }, status=400)
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(instance=user).data
        })

    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key="ip", rate="3/s", method="POST", block=True))
    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=400)
        user = serializer.save()
        django_login(request, user)

        return Response({
            'success': True,
            'user': UserSerializer(user).data,
        }, status=201)


class UserProfileViewSet(viewsets.GenericViewSet, viewsets.mixins.UpdateModelMixin,):
    queryset = UserProfile
    permission_classes = (permissions.IsAuthenticated, IsObjectOwner,)
    serializer_class = UserProfileSerializerForUpdate
