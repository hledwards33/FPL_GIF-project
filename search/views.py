from django.shortcuts import render
from django.http import HttpResponse
import os
import pandas as pd
import requests
import json
import bar_chart_race as bcr
from moviepy.editor import VideoFileClip

league_url = 'https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings'
manager_url = 'https://fantasy.premierleague.com/api/entry/{manager_id}/history/'


# url code
def home(request):
    return render(request, "search/home.html")

def search(request):
    return render(request, "search/search.html")


# FPL GIF Code
def get_league_id(Mini_league_url):
    league_id = Mini_league_url[Mini_league_url.find('leagues/') + 8:]
    league_id = league_id[:league_id.find('/')]

    return league_id


def league_data(league_id, league_url, phase_number=1):
    query_string = '?phase={phase_number}'.format(phase_number=phase_number)
    league_url = league_url + '/' + query_string

    response = requests.get(league_url)
    response = json.loads(response.content)

    league_name = response['league']['name']
    league_start = response['league']['start_event']

    response = pd.DataFrame.from_dict(response['standings']['results'])

    return response, league_name, league_start


def league_list(League_Data):
    manager_id = list(League_Data['entry'])
    manager_name = list(League_Data['player_name'].apply(lambda x: x[:x.find(' ') + 2]))  # +1 adds surname initial
    manager_info = list(zip(manager_name, manager_id))

    return manager_info


def manager_info_points(manager_name, manager_id, manager_url):
    response = requests.get(manager_url.format(manager_id=manager_id))
    response = json.loads(response.content)

    data = pd.DataFrame.from_dict(response['current']).rename(columns={'event': 'GameWeek'})
    data = data.set_index('GameWeek')

    # only keep event and total points
    data = data['total_points'].rename('{manager_name}'.format(manager_name=manager_name)).to_frame()

    return data


def search_result(request):
    League_id = get_league_id(request.POST['league_url'])

    League_Data, League_name, League_start = league_data(League_id, league_url.format(
        league_id=League_id))  # this will be the name the data in saved under

    League_List = league_list(League_Data)

    d = {}
    for (i, j) in League_List:
        d['{manager_name}_Data'.format(manager_name=i)] = manager_info_points(i, j, manager_url)

    full_league_total_points = list(d.items())[0][1]  # to get correct size
    full_league_total_points = pd.DataFrame(index=full_league_total_points.index)

    for data in d.items():
        full_league_total_points = full_league_total_points.join(data[1])

    if League_start > 1:  # subtract points accrued before league start date
        normalise = full_league_total_points.iloc[League_start - 2:League_start - 1, :].fillna(0).values.tolist()[0]
        full_league_total_points = (full_league_total_points - normalise).iloc[League_start - 1:]

    full_league_rank = full_league_total_points.rank(axis=1, ascending=False).T  # rank and transpose

    full_league_total_points = full_league_total_points.T  # Transpose the data

    # bar_race(full_league_total_points.T, League_name, League_name)
    mp4_file = bcr.bar_chart_race(df=full_league_total_points.T, scale='linear',
                                  title='{league} - FPL Points by GameWeek'.format(league=League_name))

    return render(request, "search/search_result.html", {'gif_file':mp4_file})
