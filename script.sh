#!/usr/bin/env bash
# first is username second is project name

sudo -s
set -e
source /home/$1/venv/bin/activate
sudo python -m pip install django
cd /home/$1
sudo python -m django startproject $2
sudo pip install uwsgi
mv /home/$1/$2/$2 /home/$1/$2/config
deactivate