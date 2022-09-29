from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.api.serializers import UserSerializer
from django.contrib.auth import logout as django_logout


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class AccountViewSet(viewsets.ViewSet):
    # if you want to define some fuctionality on the object then detail = true
    @action(methods=['GET'], detail=False)
    def login_status(self,request):
        data = {'has_logged_in' : request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data

        return Response(data)

    @action(methods = ['POST'], detail=False)
    def logout(self,request):
        django_logout(request)
        return Response({"Success":True})

