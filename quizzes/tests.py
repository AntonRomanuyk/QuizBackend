from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from companies.models import Company

from .models import Question
from .models import Quiz
from .models import QuizResult
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
        quiz = self.quiz
        user = self.user_owner

        self.client.force_authenticate(user=user)

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

        created_result = QuizResult.objects.get(user=user, quiz=quiz)
        self.assertEqual(created_result.user, user)
        self.assertEqual(created_result.company, quiz.company)
        self.assertEqual(created_result.total_questions, quiz.quiz_questions.count())
        self.assertIn("score", response.data)
        self.assertEqual(response.data["score"], 50.0)
        self.client.force_authenticate(user=None)

    def test_quiz_attempt_with_incorrect_answers(self):

        self.client.force_authenticate(user=self.user_owner)

        Question.objects.create(
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

                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


        self.client.force_authenticate(user=None)

    def test_company_average_score(self):
        self.client.force_authenticate(user=self.user_owner)

        QuizResult.objects.create(
            user=self.user_owner,
            company=self.company,
            quiz=self.quiz,
            total_questions=10,
            correct_answers=7,
            score=70.0,
            status='completed'
        )

        url = reverse('quiz-company-average-score', args=[self.company.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_id'], self.company.id)
        self.assertEqual(response.data['total_questions'], 10)
        self.assertEqual(response.data['correct_answers'], 7)
        self.assertAlmostEqual(response.data['average_score'], 7.0, places=1)

        self.client.force_authenticate(user=None)

    def test_system_average_score(self):
        self.client.force_authenticate(user=self.user_owner)

        QuizResult.objects.create(
            user=self.user_owner,
            company=self.company,
            quiz=self.quiz,
            total_questions=10,
            correct_answers=7,
            score=70.0,
            status='completed'
        )
        another_company = Company.objects.create(name="Another Company", owner=self.user_owner)
        another_quiz = Quiz.objects.create(company=another_company, title="Another Quiz", frequency_days=7)
        QuizResult.objects.create(
            user=self.user_owner,
            company=another_company,
            quiz=another_quiz,
            total_questions=5,
            correct_answers=3,
            score=60.0,
            status='completed'
        )

        url = reverse('quiz-overall-average-score')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_questions'], 15)
        self.assertEqual(response.data['correct_answers'], 10)
        self.assertAlmostEqual(response.data['average_score'], 6.67, places=2)

        self.client.force_authenticate(user=None)
