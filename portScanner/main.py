import socket
import sys
from datetime import datetime


if len(sys.argv == 2):

    target = socket.gethostbyname(sys.argv[1])
else:

    print("Invalid amount of arguments provided.")
    print("Syntax is: python3 <name_of_file>.py <ip>")


print("-" * 50)
print("Scanning target "+target)
print("Time started: "+str(datetime.now()))
print("-" * 50)


try:
    for port in range(50, 85):

        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect_ex returns a value 1 for open and 0 for close
        port_num = tcp.connect_ex(target, port)

        if port_num == 1:
            print(f"Port: {port_num} is open")
        else:
            print(f"Port: {port_num} is close")
except KeyboardInterrupt:

    print("Script interrupted by a keyboard action.")
    sys.exit()

except socket.gaierror:
    print("Hostname could not be resolved.")
    sys.exit()

except socket.error:
    print("Could not connect to server.")
    sys.exit()
