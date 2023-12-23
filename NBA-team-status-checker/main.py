import requests
from icecream import ic
from datetime import datetime
import json
from bs4 import BeautifulSoup

nickname_teams = []

url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
response = requests.get(url)

# Get current-date
current_date = datetime.now()

# Format the date in YYYY-MM-DD
formatted_date = current_date.strftime("%Y-%m-%d")



if response.status_code == 200:
  
  f = open(f"todays-game-{formatted_date}", "w")
  
  # Converts JSON-formatted content of HTTP response into a Python Object so we can work with it
  data = json.loads(response.text)
  games_today = data['events']

  for game in games_today:
      
      # Print what teams are playing today
      game_title = game['name']
      
      # Home overall record and its home game record
      team_home_name = game['competitions'][0]['competitors'][0]['team']['name']
      team_standings_overall_home = game['competitions'][0]['competitors'][0]['records'][0]['summary']
      team_home_standings = game['competitions'][0]['competitors'][0]['records'][1]['summary']
        
      team_away_name = game['competitions'][0]['competitors'][1]['team']['name']
      team_standings_overall_away = game['competitions'][0]['competitors'][1]['records'][0]['summary']
      team_away_standings = game['competitions'][0]['competitors'][1]['records'][2]['summary']

      nickname_teams.append(game['competitions'][0]['competitors'][0]['team']['location'])
      nickname_teams.append(game['competitions'][0]['competitors'][1]['team']['location'])
        
      print("\n", file=f)
      print("----------------------------------------------", file=f)
      print(f"Game Title: {game_title}", file=f)
      print(f"The Home Team: {team_home_name} have an overall record of {team_standings_overall_home} and has a home record of {team_home_standings}", file=f)
      print(f"The Visiting Team: {team_away_name} have an overall record of {team_standings_overall_away} and has a road record of {team_away_standings}", file=f)


 

  columns = ['Player', 'Position', 'Game Date', 'Injury Type', 'Expected Return']


  url = 'https://www.cbssports.com/nba/injuries/'
  response = requests.get(url)


  if response.status_code == 200:
      # Parse the HTML content
      soup = BeautifulSoup(response.text, 'html.parser')
      
      # This will return all divs with the specified class into a list MAKING this the PARENT CONTAINER
      # This container info contains the nba team name, and a table that holds player name and their INJURIES
      lists = soup.find_all("div", {"class": "TeamLogoNameLockup-nameContainer"})

      for items in lists:
          
          # Find a specific element under the parent container element and EXTRACT TEXT
          team_abbr = items.find('a') 
          team_name = team_abbr.text.strip()
        
          # Get all injured players on teams playing today 
          if team_name in nickname_teams:
              print("\n", file=f)
              print("----------------------------------------------", file=f)
              print("Team", team_name, "Injury List:", file=f)
              print(' | '.join(columns), file=f)
          
              # Find the table within the div
              table = items.find_next('table', {"class": "TableBase-table"})

              # Check if the table is found
              if table:
                  # Find all rows in the table body
                  rows = table.find('tbody').find_all('tr')

                  # Iterate over each row and extract values
                  for row in rows:
                      # Find all cells in the row
                      cells = row.find_all('td')

                      # Extract and print the text content of each cell
                      values = [cell.get_text(strip=True) for cell in cells]
                      print(' | '.join(values), file=f)
              else:
                  print("Table not found for", team_name)
  f.close()
else:
    
    print("API not working please try again later.")
      


       
            
          
            
            
            

            

    
    
   
   
    



