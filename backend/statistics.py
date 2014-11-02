import leagueoflegends as leagueapi
import time
import database as db

lol = leagueapi.LeagueOfLegends("a11424c1-eb9b-470c-8405-d52ef58c5a67")


def get_common_games_in_history(summoner_ids):

  if len(summoner_ids) < 2:
    return

  firstGames = lol.get_summoner_games(next(iter(summoner_ids)))
  commonGames = []
  for game in firstGames:
    common = 0
    for player in game["fellowPlayers"]:
      if player["summonerId"] in summoner_ids:
        common += 1

    if common == len(summoner_ids) - 1:
      commonGames.append(game["gameId"])

  return commonGames


def get_stats_of_games(summoner_ids_names, match_ids, excluded_game_ids):

  playerStats = {}
  for player in summoner_ids_names:
    playerStats[player] = {}

    playerStats[player]["championsKilled"] = 0
    playerStats[player]["numDeaths"] = 0
    playerStats[player]["assists"] = 0
    playerStats[player]["minionsKilled"] = 0
    playerStats[player]["doubleKills"] = 0
    playerStats[player]["tripleKills"] = 0
    playerStats[player]["qudraKills"] = 0
    playerStats[player]["pentaKills"] = 0
    playerStats[player]["totalGames"] = 0

  for player in summoner_ids_names:
    lastTenGames = lol.get_summoner_games(summoner_ids_names[player])
    for game in lastTenGames:
      gameId = game["gameId"]
      if gameId in match_ids and gameId not in excluded_game_ids:
        stats = game["stats"]

        playerStats[player]["championsKilled"] += stats.get("championsKilled", 0)
        playerStats[player]["numDeaths"] += stats.get("numDeaths", 0)
        playerStats[player]["assists"] += stats.get("assists", 0)
        playerStats[player]["minionsKilled"] += stats.get("minionsKilled", 0)
        playerStats[player]["doubleKills"] += stats.get("doubleKills", 0)
        playerStats[player]["tripleKills"] += stats.get("tripleKills", 0)
        playerStats[player]["qudraKills"] += stats.get("qudraKills", 0)
        playerStats[player]["pentaKills"] += stats.get("pentaKills", 0)
        playerStats[player]["totalGames"] += 1

  return playerStats


def update_stats(group_id=None):
  if group_id == None:
    all_groups = db.get_all_groups()
  else:
    all_groups = [group_id]

  for group_id in all_groups:
    already_tracked_games = db.get_tracked_match_ids(group_id)
    group_data = db.get_group_data(group_id)
    name_ids = {}
    for player in group_data:
      name_ids[player] = group_data[player]["summonerId"]

    common_matches = get_common_games_in_history(name_ids)
    stats = get_stats_of_games(name_ids, common_matches, already_tracked_games)
    for stat in stats:
      group_data["stats"][stat] += stats[stat]

    db.update_group_data(group_id, group_data)
    db.add_tracked_matches(group_id, common_matches)

  return


def auto_refresh_stats():
  while True:
    try
      update_stats()
      print("Updated stats at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    except Exception as e:
      print(e)

    time.sleep(15)

  return


if __name__ == "__main__":
  auto_refresh_stats()

  # balajiId = lol.get_summoner_id_from_name("PulseFire Annie")
  # patrickId = lol.get_summoner_id_from_name("BasicBananas")

  # commonGames = get_common_games_in_history([balajiId, patrickId])

  # print(get_stats_of_games({"BasicBananas" : patrickId, "PulseFire Annie" : balajiId}, commonGames, set([])))
