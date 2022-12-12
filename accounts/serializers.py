from rest_framework import serializers
from .models import User



class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'password2'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        del validated_data['password2']
        return User.objects.create_user(**validated_data)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('passwords must match')
        return data

