from django.shortcuts import render, redirect

# Create your views here.
def no_permission(request):
    return render(request, 'no-permission.html')