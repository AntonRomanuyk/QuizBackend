from django.contrib import admin

from .models import Question
from .models import Quiz


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'created_at']
    search_fields = ['title', 'company__name']
    list_filter = ['created_at', 'company']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz']
    search_fields = ['text', 'quiz__title']

