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

