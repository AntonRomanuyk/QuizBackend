from django.utils.translation import gettext as _
from rest_framework import serializers

from .models import Question
from .models import Quiz
from .models import QuizResult


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


class QuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResult
        fields = ['id', 'user', 'company', 'quiz', 'score', 'total_questions',
                  'correct_answers', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class QuizAttemptSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    answers = serializers.ListField(
        child=serializers.JSONField(),
    )

    def validate(self, data):
        quiz_id = data['quiz_id']
        answers = data['answers']
        quiz = Quiz.objects.prefetch_related('quiz_questions').filter(id=quiz_id).first()
        if not quiz:
            raise serializers.ValidationError(_("Quiz does not exist."))

        expected_question_count = quiz.quiz_questions.count()
        if len(answers) != expected_question_count:
            raise serializers.ValidationError(_("All questions must be answered. "
                                                "Expected: %(expected)s, Received: %(received)s.") % {
                    "expected": expected_question_count,
                    "received": len(answers)
                })
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        quiz = Quiz.objects.prefetch_related('quiz_questions').get(id=validated_data['quiz_id'])
        company = quiz.company
        questions = {question.id: question for question in quiz.quiz_questions.all()}
        total_questions = len(questions)
        correct_answers = 0

        for answer in validated_data['answers']:
            question_id = answer['question_id']
            selected_answer = answer['selected_answer']

            question = questions.get(question_id)
            if not question:
                raise serializers.ValidationError(_(f"Invalid question ID: {question_id}"))
            if question.correct_answer == selected_answer:
                correct_answers += 1

        score = correct_answers / total_questions * 100

        quiz_result = QuizResult.objects.create(
            user=user,
            company=company,
            quiz=quiz,
            score=score,
            total_questions=total_questions,
            correct_answers=correct_answers,
            status = 'completed'
        )
        return quiz_result
