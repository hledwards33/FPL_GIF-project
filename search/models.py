from django.db import models
import os
import pandas as pd
import requests
import json
import bar_chart_race as bcr
from moviepy.editor import VideoFileClip

class Search(models.Model):
    url = models.CharField(max_length=500,default='https://fantasy.premierleague.com/leagues/314/standings/c')
    image = models.ImageField(upload_to='images/', null=True)

    # set User-Defined variables
    Mini_league_url = 'https://fantasy.premierleague.com/leagues/328119/standings/c'  # change this to the league we want to analyse

    # set the Global variables
    league_url = 'https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings'
    manager_url = 'https://fantasy.premierleague.com/api/entry/{manager_id}/history/'

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

    def bar_race(data, filename, league_name="Your League"):

        bcr.bar_chart_race(df=data, filename='{filename}_League_BarChartRace.mp4'.format(filename=filename),
                           scale='linear', title='{league} - FPL Points by GameWeek'.format(league=league_name))

        clip = (VideoFileClip(os.path.join(os.getcwd(),
                                           '{filename}_League_BarChartRace.mp4'.format(filename=filename))))
        clip.write_gif('{filename}_League_BarChartRace.gif'.format(filename=filename))

    def create_gif():

        League_id = get_league_id(Mini_league_url)

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

        dir_path = os.getcwd()

        path_or_buf_pnts = os.path.join(dir_path, League_name + '_Total_Points_Data.csv')
        path_or_buf_rank = os.path.join(dir_path, League_name + '_Rank_Data.csv')

        full_league_total_points.to_csv(path_or_buf=path_or_buf_pnts)
        full_league_rank.to_csv(path_or_buf=path_or_buf_rank)

        bar_race(full_league_total_points.T, League_name, League_name)


