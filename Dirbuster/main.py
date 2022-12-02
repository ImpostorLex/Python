import ipaddress
from click import FileError
import typer
import os.path
from icmplib import ping

app = typer.Typer()
get_ip = ""

@app.command(short_help="REQUIRED [URL] + [WORDLIST PATH] e.g http://127.0.0.1/ /usr/wordlist/rockyou.txt")
def d(url:str, path:str):
    
    # check if url is valid.
    if url[0:8] == "https://" and url[-1] == "/":
        get_ip = url[8:-1].strip("/")
        

    elif url[0:7] == "http://" and url[-1] == "/":
        get_ip = url[7:-1].strip("/")
        
        
    else:
        typer.echo("Invalid schema maybe, check again.")
    
    try: 
        is_ip = ipaddress.ip_address(get_ip)
        is_file_exists = os.path.exists(path)

        if is_file_exists is False:
            raise FileError

    except ValueError:
        typer.echo("Is not valid IP")
    
    except FileError:
        typer.echo("File does not exists or not a text file.")
    
    else:
        ctr = 0
        word = open(path, "r")
        wordlists = word.readlines()

        for word in wordlists:
            dirb = url + wordlists[ctr]
            x = ping(dirb, count=4, id=None, privileged=True)
            ctr = ctr + 1          
            typer.echo(x.is_alive)


if __name__ == "__main__":
    app()