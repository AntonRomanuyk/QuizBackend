from django.contrib import admin

from companies.models import Company
from companies.models import CompanyInvitation
from companies.models import CompanyRequest


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_visible")
    search_fields = ("name", "owner__username")
    list_filter = ("is_visible",)
    ordering = ("name",)
    filter_horizontal = ("members",)

@admin.register(CompanyInvitation)
class CompanyInvitationAdmin(admin.ModelAdmin):
    list_display = ("company", "user", "status", "created_at", "updated_at")
    search_fields = ("company__name", "user__username")
    list_filter = ("status",)
    ordering = ("-created_at",)

@admin.register(CompanyRequest)
class CompanyRequestAdmin(admin.ModelAdmin):
    list_display = ("company", "user", "status", "created_at", "updated_at")
    search_fields = ("company__name", "user__username")
    list_filter = ("status",)
    ordering = ("-created_at",)

