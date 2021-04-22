from django.shortcuts import render

def graphs(request):
    return render(request, "charts/graphs.html")

def graphs_result(request):
    return render(request, "charts/graphs_result.html")
