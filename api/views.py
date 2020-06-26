# from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from api.serializers import RegistrationSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

User = get_user_model()


class UserAPIView(GenericViewSet):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer
    queryset = User.objects.all()
    lookup_field = 'pk'

    def create(self, request, *args, **kwargs):
        data = request.data
        print(f"data: {data}")
        serializer = RegistrationSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(validated_data=serializer.validated_data)
            return Response({"user": user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
