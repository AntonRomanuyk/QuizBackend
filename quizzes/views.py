from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from companies.permissions import IsCompanyAdminOrOwner

from .models import Quiz
from .serializers import QuizSerializer


# Create your views here.
class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all().prefetch_related('quiz_questions')
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyAdminOrOwner]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def company_quizzes(self, request, company_pk=None):
        quizzes = self.get_queryset().filter(company_id=company_pk)
        serializer = self.get_serializer(quizzes, many=True)
        return Response(serializer.data)
