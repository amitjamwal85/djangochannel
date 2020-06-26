from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from justchat.models import GENDER

User = get_user_model()


def password_field():
    return serializers.CharField(
        max_length=32,
        min_length=8,
        required=True
    )


def required_field():
    return serializers.CharField(required=True)


def required_and_valid(value):
    if value is None:
        raise serializers.ValidationError('This field is required')
    return True


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[required_and_valid, UniqueValidator(queryset=User.objects.all())])
    password = password_field()
    first_name = required_field()
    last_name = required_field()
    gender = serializers.ChoiceField(required=True, choices=GENDER)
    profile_image = serializers.FileField(required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'gender', 'profile_image']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
