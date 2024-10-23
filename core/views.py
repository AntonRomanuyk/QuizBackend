from django.shortcuts import render
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    })
# Create your views here.
