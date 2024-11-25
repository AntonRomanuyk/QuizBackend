from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .models import User
from .serializers import UserListSerializer
from .serializers import UserSerializer


# Create your views here.
class UserPagination(PageNumberPagination):
    page_size = 10


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        return UserSerializer


