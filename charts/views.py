from django.shortcuts import render

def graphs(request):
    return render(request, "charts/graphs.html")
