from django.shortcuts import render
import json
import requests

url = "https://fantasy.prmeierleague.com/api/bootstrap-static/"
photo_url = "https://resources.premierleague.com/premierleague/photos/players/110x140/p{photo_num}.png"

def analysis(request):
    return render(request, 'form/analysis.html')

def get_player_data():
    response = requests.get(url)
    response = response.json()
    elements = response['elements']

    d = {}
    for i in range(len(elements)):
        d[i] = elements[i]['form']

    d = dict(sorted(d.items(), key=lambda item: item[1], reverse=True))

    l=[]
    for i in range(11):
        index = list(d.keys())[i]
        l.append(elements[index])