from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Company
from .models import CompanyInvitation
from .models import CompanyRequest


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username']

class CompanySerializer(serializers.ModelSerializer):
    members = UserSummarySerializer(many=True, required=False)
    admins = UserSummarySerializer(many=True, required=False)

    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'is_visible', 'owner', 'members','admins', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']

class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'is_visible', 'created_at']

class CompanyInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyInvitation
        fields = ['id', 'company', 'user', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class CompanyInvitationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyInvitation
        fields = ['id', 'company', 'user', 'status', 'created_at']


class CompanyRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyRequest
        fields = ['id', 'company', 'user', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class CompanyRequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyRequest
        fields = ['id', 'company', 'user', 'status', 'created_at']
