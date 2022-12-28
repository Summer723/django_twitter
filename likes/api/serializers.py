from accounts.api.serializers import UserSerializer
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from likes.models import Like
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(source="cached_user")

    class Meta:
        model = Like
        fields = ("user", "created_at")


class BaseLikeSerializerForCreateAndCancel(serializers.ModelSerializer):
    # it takes two things
    content_type = serializers.ChoiceField(["comment", "tweet"])
    object_id = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ('content_type', 'object_id')

    def _get_model_class(self, data):
        if data['content_type'] == "comment":
            return Comment
        if data['content_type'] == "tweet":
            return Tweet
        return None

    def validate(self, data):
        # check whether the object exists
        # check whether the content type is correct
        if data['content_type'] not in ["comment", 'tweet']:
            raise ValidationError({'content_type': 'Content type does not exist'})
        model_class = self._get_model_class(data)
        liked_object = model_class.objects.filter(id = data['object_id']).first()
        if liked_object is None:
            raise ValidationError({"object_id": 'Object does not exist!'})
        return data


class LikeSerializerForCreate(BaseLikeSerializerForCreateAndCancel):
    def get_or_create(self):
        validated_data = self.validated_data
        model_class = self._get_model_class(validated_data)
        return  Like.objects.get_or_create(
            # ContentType.objects.get_for_model get the content type of the class
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=validated_data['object_id'],
            user=self.context['request'].user,
        )


class LikeSerializerForCancel(BaseLikeSerializerForCreateAndCancel):
    def cancel(self):
        model_class = self._get_model_class(self.validated_data)
        deleted, _ = Like.objects.filter(
            # ContentType.objects.get_for_model get the content type of the class
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=self.validated_data['object_id'],
            user=self.context['request'].user,
        ).delete()
        return deleted




