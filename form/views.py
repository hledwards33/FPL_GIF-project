from django.shortcuts import render

def analysis(request):
    return render(request, 'form/analysis.html')
