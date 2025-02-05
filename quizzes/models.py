from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Quiz(TimeStampedModel):
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='company_quizzes'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    frequency_days = models.PositiveIntegerField()

    def __str__(self):
        return self.title

class Question(TimeStampedModel):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='quiz_questions'
    )
    text = models.CharField(max_length=255)
    options = models.JSONField()
    correct_answer = models.PositiveIntegerField()
    allow_multiple_answers = models.BooleanField(default=False)

    def __str__(self):
        return f"Question: {self.text} (Quiz: {self.quiz.title})"


class QuizResult(TimeStampedModel):
    class StatusChoices(models.TextChoices):
        STARTED = 'started', 'Started'
        COMPLETED = 'completed', 'Completed'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quizzes')
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='quiz_results')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    score = models.FloatField(null=True, blank=True)
    total_questions = models.PositiveIntegerField(null=True, blank=True)
    correct_answers = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.STARTED)

    def __str__(self):
        return f"User: {self.user.username} (Quiz: {self.quiz.title} by {self.company.name})"
