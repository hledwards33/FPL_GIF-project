from django.shortcuts import render
import pandas as pd
import requests
import json
from collections import Counter
import itertools
import plotly.graph_objects as go
import plotly.offline

league_url = 'https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings'
manager_url = 'https://fantasy.premierleague.com/api/entry/{manager_id}/history/'
team_url = "https://fantasy.premierleague.com/api/entry/{manager_id}/event/{GW}/picks/"
player_url = "https://fantasy.premierleague.com/api/element-summary/{player_id}/"
master_url = "https://fantasy.premierleague.com/api/bootstrap-static/"


def graphs(request):
    return render(request, "charts/graphs.html")


# FPL code
def get_league_id(Mini_league_url):
    league_id = Mini_league_url[Mini_league_url.find('leagues/') + 8:]
    league_id = league_id[:league_id.find('/')]

    return league_id


def league_data(league_url, phase_number=1):
    query_string = '?phase={phase_number}'.format(phase_number=phase_number)
    league_url = league_url + '/' + query_string

    response = requests.get(league_url)
    response = json.loads(response.content)

    r = response['league']
    league_name = response['league']['name']
    league_start = response['league']['start_event']

    response = pd.DataFrame.from_dict(response['standings']['results'])

    return response, league_name, league_start


def league_list(League_Data):
    manager_id = list(League_Data['entry'])
    return manager_id


def manager_info_points(manager_id, manager_url):
    response = requests.get(manager_url.format(manager_id=manager_id))
    response = json.loads(response.content)

    gameweek = response['current'][-1]['event']

    return gameweek


def get_manager_picks(manager_id, gameweek):
    response = requests.get(team_url.format(manager_id=manager_id, GW=gameweek))
    response = json.loads(response.content)
    picks = response['picks']

    return picks


def graphs_result(request):
    league_id = get_league_id(request.POST['league_url'])

    league_Data, league_name, league_start = league_data(league_url.format(league_id=league_id))

    manager_ids = league_list(league_Data)

    gameweek = manager_info_points(904781, manager_url)

    # get all managers teams
    picks = []
    for i in range(len(manager_ids)):
        picks.append(get_manager_picks(manager_ids[i], gameweek))

    # get list of all players
    players = []
    for i in range(len(picks)):
        for j in range(len(picks[i])):
            players.append(picks[i][j]['element'])

    # make id to name dictionary
    player_dict = {}
    p_response = requests.get(master_url).json()['elements']
    for i in range(len(p_response)):
        player_dict[p_response[i]['id']] = p_response[i]['first_name'] + ' ' + p_response[i]['second_name']

    player_name = []
    for i in range(len(players)):
        player_name.append(player_dict[players[i]])

    # sort list by frequency
    sorted_player_name = [item for items, c in Counter(player_name).most_common() for item in [items] * c]

    # convert to dict with player count
    player_freq = {}
    for item in sorted_player_name:
        if (item in player_freq):
            player_freq[item] += 1
        else:
            player_freq[item] = 1

    # slice dict for top 10 and bottom 10
    if len(player_freq) > 10:
        players_top10 = dict(itertools.islice(player_freq.items(), 10))
        players_bottom10 = dict(itertools.islice(player_freq.items(), len(player_freq) - 10, len(player_freq)))
    else:
        players_top10 = player_freq
        players_bottom10 = player_freq

    labels = list(players_top10.keys())
    values = list(players_top10.values())
    fig_top_10 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.25)])
    fig_top_10_html = plotly.offline.plot(fig_top_10, auto_open=False, output_type="div")

    return render(request, "charts/graphs_result.html", {'top_10':fig_top_10_html})
