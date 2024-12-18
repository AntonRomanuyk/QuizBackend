from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from companies.models import Company

from .models import Question
from .models import Quiz
from .models import TestResult
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

        self.question1 = Question.objects.create(
            quiz=self.quiz,
            text="What is 2 + 2?",
            options=[2, 4, 5],
            correct_answer=4,
            allow_multiple_answers=False
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

    def test_quiz_attempt(self):

        self.client.force_authenticate(user=self.user_owner)

        question2 = Question.objects.create(
            quiz=self.quiz,
            text="Sample Question 2",
            options=["Option 1", "Option 2", "Option 3"],
            correct_answer=2,
            allow_multiple_answers=False,
        )

        response = self.client.post(
            reverse("quiz-attempt", args=[self.quiz.id]),
            data={
                "quiz_id": self.quiz.id,
                "answers": [
                    {"question_id": self.question1.id, "selected_answer": self.question1.correct_answer},
                    {"question_id": question2.id, "selected_answer": 0},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIn("score", response.data)
        self.assertEqual(response.data["score"], 50.0)
        self.client.force_authenticate(user=None)


    def test_analytics(self):
        self.client.force_authenticate(self.user_owner)

        TestResult.objects.create(user=self.user_owner, company=self.company, quiz=self.quiz,
                                  total_questions=10, correct_answers=7, score=70.0)
        TestResult.objects.create(user=self.user_owner, company=self.company, quiz=self.quiz,
                                  total_questions=5, correct_answers=3, score=60.0)

        response = self.client.get(reverse('quiz-analytics'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('average_score', response.data)
        self.assertEqual(response.data['total_tests'], 2)
        self.assertEqual(response.data['total_questions'], 15)
        self.assertEqual(response.data['correct_answers'], 10)
        self.assertAlmostEqual(response.data['average_score'], 6.67, places=2)
