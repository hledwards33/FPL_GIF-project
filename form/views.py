from django.shortcuts import render
import json
import requests

photo_url = "https://resources.premierleague.com/premierleague/photos/players/110x140/p{photo_num}.png"

url = "https://fantasy.premierleague.com/api/bootstrap-static/"


def analysis(request):
    player_data = get_player_data()
    return render(request, 'form/analysis.html', {'player_data': player_data})


def get_player_data():
    response = requests.get(url)
    response = json.loads(response.content)
    elements = response['elements']

    all_data = {}
    for i in range(len(elements)):
        all_data[i] = elements[i]['form']

    all_data = dict(sorted(all_data.items(), key=lambda item: item[1], reverse=True))

    player_dict = {}
    for i in range(11):
        index = list(all_data.keys())[i]
        player_dict[i] = {'form': elements[index]['form'],
                          'name': elements[index]['first_name'] + " " + elements[index]['second_name'],
                          'news': elements[index]['news'],
                          'dreamteam apps': elements[index]['dreamteam_count'],
                          'selected by ': elements[index]['selected_by_percent'],
                          'bp total': elements[index]['bonus'],
                          'photo': elements[index]['photo'][:-4],
                          'points': elements[index]['total_points'],
                          'chance of playing': elements[index]['chance_of_playing_next_round'],
                          'transfers in': elements[index]['transfers_in_event'],
                          'transfers out': elements[index]['transfers_out_event'],
                          'goals': elements[index]['goals_scored'],
                          'assists': elements[index]['assists'],
                          'clean sheets': elements[index]['clean_sheets'],
                          'cost': elements[index]['now_cost'] / 10
                          }
        return player_dict
