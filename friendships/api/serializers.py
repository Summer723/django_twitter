from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from friendships.services import FriendshipService

class FollowerSerializer(serializers.ModelSerializer):
    # source = "from_user" ===> model.from_user
    user = UserSerializerForFriendship(source="from_user")
    created_at = serializers.DateTimeField()
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ["user", 'created_at', 'has_followed']

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return FriendshipService.has_followed(self.context['request'].user, obj.from_user)


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source="to_user")
    created_at = serializers.DateTimeField()
    has_followed = serializers.SerializerMethodField()


    class Meta:
        model = Friendship
        fields = ["user", 'created_at', "has_followed"]

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return FriendshipService.has_followed(self.context['request'].user, obj.to_user)

class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')
    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message' : 'from_user_id and to_user_id should be different',
            })
        if Friendship.objects.filter(
            from_user_id=attrs['from_user_id'],
            to_user_id=attrs['to_user_id'],
        ).exists():
            raise ValidationError({
                'message': 'You have already followed the user!',
            })
        return attrs

    def create(self, validated_data):
        return Friendship.objects.create(
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id'],
        )
