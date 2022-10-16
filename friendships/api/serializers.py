from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class FollowerSerializer(serializers.ModelSerializer):
    # source = "from_user" ===> model.from_user
    user = UserSerializerForFriendship(source="from_user")
    created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ["user", 'created_at']


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source="to_user")
    created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ["user", 'created_at']