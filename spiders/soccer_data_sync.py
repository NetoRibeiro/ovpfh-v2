import soccerdata as sd

fbref = sd.FBref()
season_stats = fbref.read_team_season_stats(stat_type='shooting')

print(season_stats)

fbref = sd.FBref(leagues=['ENG-Premier League'], seasons=['1718', '1819'])

season_stats = fbref.read_team_season_stats(stat_type='shooting')

print(season_stats)
