import requests
from bs4 import BeautifulSoup
import sys, os


def app():
    data = []
    crypto = sys.argv[1]
    sites = [f"https://www.coingecko.com/en/coins/{crypto}", "https://www.xe.com/currencyconverter/convert/?Amount=1&From=USD&To=PHP"]
    
    session = requests.Session()

    for site in sites:
        response = session.get(site)

        if (response.status_code >= 400):
            os.system('clear')
            print(f"An error has occured maybe {crypto} doesn't exist")
            return ""          
        else:
            data.append(response.text)
    
    for dt in data:
            soup = BeautifulSoup(dt, 'html.parser')
                
            try:
                usd = soup.find("span", {"class": "no-wrap"}).get_text().replace("$", "").replace(",", "")          
                     
            except:
                php = soup.find("p", {"class": "result__BigRate-sc-1bsijpp-1 iGrAod"}).get_text().replace("Philippine Pesos", "")
                    
        
    
    convert_to_php = float(usd) * float(php)
    capitalize = crypto.capitalize()
    os.system('clear')
    print(f"{capitalize} in dollars: ${usd}\n{capitalize} in pesos: ₱{convert_to_php}")


if __name__ == '__main__':
   app()
   
