import ipaddress
from click import FileError
from importlib_metadata import distributions
import typer
from pythonping import ping
from ipaddress import ip_address
import os.path

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
        typer.echo("Invalid schema maybe check again.")
    
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
        with open(path, "r") as word:
            wordlists = word.readlines()
            dirb = url + wordlists[ctr]
            typer.echo(dirb)
            # ping(dirb, verbose=True)
            #  ctr = ctr + 1
        
        

if __name__ == "__main__":
    app()