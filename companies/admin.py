from django.contrib import admin

from .models import Company


# Register your models here.
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description']
    list_filter = ['is_visible', 'created_at']
    list_display = ['name', 'owner', 'is_visible', 'created_at']
