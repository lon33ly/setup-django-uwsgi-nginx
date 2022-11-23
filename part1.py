import os
import socket

hostname = socket.gethostname()
ipv4 = socket.gethostbyname(hostname)
username = os.getlogin()

os.system('sudo apt-get update')
os.system('sudo apt-get upgrade')
os.system('sudo apt update && sudo apt upgrade -y')
os.system('sudo apt install software-properties-common -y')
os.system('sudo add-apt-repository ppa:deadsnakes/ppa')

python3_x_version = str(input("Python 3.x version (input x): "))

os.system(f'sudo apt install python3.{python3_x_version}')
os.system('sudo apt install python3-pip')
os.system('sudo pip3 install virtualenv')
os.system(f'sudo python3 -m virtualenv -p="/usr/bin/python3.{python3_x_version}" /home/{username}/venv')
os.system(f'sudo apt-get install python3.{python3_x_version}-dev')
os.system(f'sudo apt-get install gcc')
os.system(f'sudo apt install nginx')

