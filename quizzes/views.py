from django.db.models import Sum
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from companies.permissions import IsCompanyAdminOrOwner

from .models import Quiz
from .models import TestResult
from .paginations import QuizPagination
from .serializers import QuizAttemptSerializer
from .serializers import QuizSerializer
from .serializers import TestResultSerializer


# Create your views here.
class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all().prefetch_related('quiz_questions')
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyAdminOrOwner]
    pagination_class = QuizPagination

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def company_quizzes(self, request, company_pk=None):
        quizzes = self.get_queryset().filter(company_id=company_pk)
        serializer = self.get_serializer(quizzes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def attempt(self, request, pk=None):
        serializer = QuizAttemptSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        test_result = serializer.save()
        return Response(TestResultSerializer(test_result).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def analytics(self, request):
        user = request.user
        test_results = TestResult.objects.filter(user=user).aggregate(
        total_questions=Sum('total_questions'),
        correct_answers=Sum('correct_answers'),
    )
        total_questions = test_results['total_questions']
        correct_answers = test_results['correct_answers'] or 0
        average_score = correct_answers / total_questions * 10

        return Response({
            'total_tests': TestResult.objects.filter(user=user).count(),
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'average_score': round(average_score, 2)
        })
