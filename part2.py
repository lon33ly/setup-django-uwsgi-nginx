import os
import socket


hostname = socket.gethostname()
ipv4 = socket.gethostbyname(hostname)
username = os.getlogin()

project_name = str(input("Input name of project"))

os.system(f'source script.sh {username} {project_name}')

os.system(f'rm -f /home/{username}/{project_name}/config/settings.py')
os.system(f'cp settings.py /home/{username}/{project_name}/config/')

site_config = u'upstream django {\n' \
    f'    server unix:///home/{username}/{project_name}/{project_name}.sock;\n' \
    u'}\n' \
    u'\n' \
    f'# configuration of the server\n' \
    u'server {\n' \
    f'    listen      80;\n' \
    f'    server_name {ipv4};\n' \
    f'    charset     utf-8;\n' \
    f'    # max upload size\n' \
    f'    client_max_body_size 75M;\n' \
    f'    # Django media and static files\n' \
    u'    location /media  {\n' \
    f'        alias /home/{username}/{project_name}/media;\n' \
    u'    }\n' \
    u'    location /static {\n' \
    f'          alias /home/{username}/{project_name}/static;\n' \
    u'    }\n' \
    f'    # Send all non-media requests to the Django server.\n' \
    u'    location / {\n' \
    f'        uwsgi_pass  django;\n' \
    f'        include     /home/{username}/{project_name}/uwsgi_params;\n' \
    u'    }\n' \
    u'}\n'

uwsgi_params = """
uwsgi_param  QUERY_STRING       $query_string;
uwsgi_param  REQUEST_METHOD     $request_method;
uwsgi_param  CONTENT_TYPE       $content_type;
uwsgi_param  CONTENT_LENGTH     $content_length;
uwsgi_param  REQUEST_URI        $request_uri;
uwsgi_param  PATH_INFO          $document_uri;
uwsgi_param  DOCUMENT_ROOT      $document_root;
uwsgi_param  SERVER_PROTOCOL    $server_protocol;
uwsgi_param  REQUEST_SCHEME     $scheme;
uwsgi_param  HTTPS              $https if_not_empty;
uwsgi_param  REMOTE_ADDR        $remote_addr;
uwsgi_param  REMOTE_PORT        $remote_port;
uwsgi_param  SERVER_PORT        $server_port;
uwsgi_param  SERVER_NAME        $server_name;
"""

with open(f'/etc/nginx/sites-available/{project_name}.conf', 'w') as f:
    f.write(site_config)


with open(f'/home/{username}/{project_name}/uwsgi_params', 'w') as f:
    f.write(uwsgi_params)

os.system(f'sudo ln -s /etc/nginx/sites-available/{project_name}.conf /etc/nginx/sites-enabled/')
os.system(f'source /home/{username}/venv/bin/activate && '
          f'/home/{username}/venv/bin/python /home/{username}/{project_name}/config/manage.py collectstatic')
os.system(f'sudo /etc/init.d/nginx restart')

project_uwsgi_ini = """
[uwsgi]
# full path to Django project's root directory
chdir            = /home/{username}/{project_name}/
# Django's wsgi file
module           = config.wsgi
# full path to python virtual env
home             = /home/{username}/venv
# enable uwsgi master process
master          = true
# maximum number of worker processes
processes       = 10
# the socket (use the full path to be safe
socket          = /home/{username}/{project_name}/{project_name}.sock
# socket permissions
chmod-socket    = 666
# clear environment on exit
vacuum          = true
# daemonize uwsgi and write messages into given log
daemonize       = /home/{username}/uwsgi-emperor.log
""".format(username=username, project_name=project_name)

with open(f'/home/{username}/{project_name}/{project_name}_uwsgi.ini', 'w') as f:
    f.write(project_uwsgi_ini)

os.system(f'mkdir /home/{username}/venv/vassals')
os.system(f'sudo ln -s /home/{username}/{project_name}/{project_name}_uwsgi.ini /home/{username}/venv/vassals/')

emperor_uwsgi_service = """
[Unit]
Description=uwsgi emperor for micro {project_name} website
After=network.target
[Service]
User={username}
Restart=always
ExecStart=/home/{username}/venv/bin/uwsgi --emperor /home/{username}/venv/vassals --uid www-data --gid www-data
[Install]
WantedBy=multi-user.target
""".format(project_name=project_name, username=username)

with open(f'/etc/systemd/system/emperor.uwsgi.service', 'w') as f:
    f.write(emperor_uwsgi_service)


os.system(f'sudo systemctl enable emperor.uwsgi.service')
os.system(f'sudo systemctl start emperor.uwsgi.service')
os.system(f'sudo systemctl status emperor.uwsgi.service')
