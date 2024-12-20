from django.db.models import Sum
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from companies.permissions import IsCompanyAdminOrOwner

from .models import Quiz
from .models import QuizResult
from .paginations import QuizPagination
from .serializers import QuizAttemptSerializer
from .serializers import QuizResultSerializer
from .serializers import QuizSerializer


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
        return Response(QuizResultSerializer(test_result).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def company_average_score(self, request, pk=None):
        user = request.user
        company_id = pk

        test_results = QuizResult.objects.filter(user=user, company_id=company_id).aggregate(
            total_correct=Sum('correct_answers'),
            total_questions=Sum('total_questions')
        )

        total_questions = test_results['total_questions'] or 0
        total_correct = test_results['total_correct'] or 0

        average_score = (total_correct / total_questions * 10) if total_questions > 0 else 0

        return Response({
            'company_id': company_id,
            'total_questions': total_questions,
            'correct_answers': total_correct,
            'average_score': round(average_score, 2)
        })

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def overall_average_score(self, request):
        user = request.user

        test_results = QuizResult.objects.filter(user=user).aggregate(
            total_correct=Sum('correct_answers'),
            total_questions=Sum('total_questions')
        )

        total_questions = test_results['total_questions'] or 0
        total_correct = test_results['total_correct'] or 0

        average_score = (total_correct / total_questions * 10) if total_questions > 0 else 0

        return Response({
            'total_questions': total_questions,
            'correct_answers': total_correct,
            'average_score': round(average_score, 2)
        })
