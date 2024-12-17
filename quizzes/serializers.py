from django.utils.translation import gettext as _
from rest_framework import serializers

from .models import Question
from .models import Quiz


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'options', 'correct_answer', 'allow_multiple_answers']

    def validate(self, data):
        if len(data.get('options', [])) < 2:
            raise serializers.ValidationError(_("Each question must have at least two answer options."))

        if data.get('correct_answer') not in data.get('options', []):
            raise serializers.ValidationError(_("The correct answer must be one of the answer options."))

        return data

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'company', 'title', 'description', 'frequency_days', 'questions', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_questions(self, value):
        if len(value) < 2:
            raise serializers.ValidationError(_("A quiz must have at least two questions."))
        return value

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        quiz = Quiz.objects.create(**validated_data)
        questions = []
        for question_data in questions_data:
            serializer = QuestionSerializer(data=question_data)
            serializer.is_valid(raise_exception=True)
            questions.append(Question(quiz=quiz, **serializer.validated_data))

        Question.objects.bulk_create(questions)
        return quiz

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)
        instance = super().update(instance, validated_data)

        if questions_data is not None:
            instance.quiz_questions.all().delete()

            questions = []
            for question_data in questions_data:
                questions.append(Question(quiz=instance, **question_data))

            Question.objects.bulk_create(questions)

        return instance
