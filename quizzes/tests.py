from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from companies.models import Company

from .models import Question
from .models import Quiz
from .serializers import QuizSerializer

User = get_user_model()

class QuizTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()


        self.user_admin = User.objects.create_user(username="admin", password="password")
        self.user_owner = User.objects.create_user(username="owner", password="password")
        self.user_other = User.objects.create_user(username="other", password="password")


        self.company = Company.objects.create(name="Test Company", owner=self.user_owner)
        self.company.admins.add(self.user_admin)


        self.quiz = Quiz.objects.create(
            company=self.company,
            title="Sample Quiz",
            description="This is a sample description.",
            frequency_days=7
        )

        self.data = {
            "title": "Valid Quiz",
            "description": "Valid Description",
            "frequency_days": 5,
            "company": self.company.id,
            "questions": [
                {
                    "text": "What is 2 + 2?",
                    "options": [2, 4, 5],
                    "correct_answer": 4,
                    "allow_multiple_answers": False
                },
                {
                    "text": "What is 3 + 3?",
                    "options": [3, 6],
                    "correct_answer": 6,
                    "allow_multiple_answers": False
                }
            ]
        }



    def test_quiz_and_question_models_and_serializer(self):


        self.assertEqual(str(self.quiz), "Sample Quiz")
        self.assertEqual(self.quiz.company, self.company)


        question = Question.objects.create(
            quiz=self.quiz,
            text="Sample Question Text",
            options=[1, 2, 3],
            correct_answer=1,
            allow_multiple_answers=False
        )
        self.assertEqual(str(question), "Question: Sample Question Text (Quiz: Sample Quiz)")
        self.assertEqual(question.quiz, self.quiz)


        serializer = QuizSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["title"], "Valid Quiz")

        invalid_data = {
            "title": "Invalid Quiz",
            "description": "Invalid Description",
            "frequency_days": 3,
            "company": self.company.id,
            "questions": [
                {
                    "text": "What is 5 + 5?",
                    "options": [10],
                    "correct_answer": 10,
                    "allow_multiple_answers": False
                }
            ]
        }
        serializer = QuizSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue("questions" in serializer.errors)
