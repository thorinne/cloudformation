# Install System Packages
yum install -y gcc python36 python36-devel python36-setuptools libxml2-devel libxslt-devel libffi-devel openssl-devel redhat-rpm-config
easy_install-3.6 pip

# Download NetBox
wget https://github.com/netbox-community/netbox/archive/vX.Y.Z.tar.gz
tar -xzf vX.Y.Z.tar.gz -C /opt
cd /opt/
ln -s netbox-X.Y.Z/ netbox
cd /opt/netbox/

# Create the NetBox User
groupadd --system netbox
adduser --system --gid netbox netbox
chown --recursive netbox /opt/netbox/netbox/media/

# Set Up Python Environment
python3 -m venv /opt/netbox/venv
source venv/bin/activate
#Now in vENV
pip3 install -r requirements.txt

# Configuration
cd netbox/netbox/
cp configuration.example.py configuration.py # Configure to copy config file from S3 bucket


# Database
# This parameter holds the database configuration details. You must define the username and password used when you configured PostgreSQL. If the service is running on a remote host, replace localhost with its address. See the configuration documentation for more detail on individual parameters.

# Example:

#DATABASE = {
#    'NAME': 'netbox',               # Database name
#    'USER': 'netbox',               # PostgreSQL username
#    'PASSWORD': 'J5brHrAXFLQSif0K', # PostgreSQL password
#    'HOST': 'localhost',            # Database server
#    'PORT': '',                     # Database port (leave blank for default)
#    'CONN_MAX_AGE': 300,            # Max database connection age
#}

# REDIS
# Redis is a in-memory key-value store required as part of the NetBox installation. It is used for features such as webhooks and caching. Redis typically requires minimal configuration; the values below should suffice for most installations. See the configuration documentation for more detail on individual parameters.

#REDIS = {
#    'tasks': {
#        'HOST': 'redis.example.com',
#        'PORT': 1234,
#        'PASSWORD': 'foobar',
#        'DATABASE': 0,
#        'DEFAULT_TIMEOUT': 300,
#        'SSL': False,
#    },
#    'caching': {
#        'HOST': 'localhost',
#        'PORT': 6379,
#        'PASSWORD': '',
#        'DATABASE': 1,
#        'DEFAULT_TIMEOUT': 300,
#        'SSL': False,
#    }
#}

# SECRET_KEY
# Generate a random secret key of at least 50 alphanumeric characters. This key must be unique to this installation and must not be shared outside the local system.

You may use the script located at netbox/generate_secret_key.py to generate a suitable key.

# Run Database Migrations
# Before NetBox can run, we need to install the database schema. This is done by running python3 manage.py migrate from the netbox directory (/opt/netbox/netbox/ in our example):

cd /opt/netbox/netbox/
python3 manage.py migrate
#Operations to perform:
#  Apply all migrations: dcim, sessions, admin, ipam, utilities, auth, circuits, contenttypes, extras, secrets, users
#Running migrations:
#  Rendering model states... DONE
#  Applying contenttypes.0001_initial... OK
#  Applying auth.0001_initial... OK
#  Applying admin.0001_initial... OK
#  ...
#If this step results in a PostgreSQL authentication error, ensure that the username and password created in the database match what has been specified in configuration.py

# Create a Super User
# NetBox does not come with any predefined user accounts. You'll need to create a super user to be able to log into NetBox:

python3 manage.py createsuperuser
#Username: admin
#Email address: admin@example.com
#Password:
#Password (again):
#Superuser created successfully.

# Collect Static Files
python3 manage.py collectstatic --no-input

# 959 static files copied to '/opt/netbox/netbox/static'.

# Test the Application
# At this point, NetBox should be able to run. We can verify this by starting a development instance:

python3 manage.py runserver 0.0.0.0:8000 --insecure

#Performing system checks...
#System check identified no issues (0 silenced).
#November 28, 2018 - 09:33:45
#Django version 2.0.9, using settings 'netbox.settings'
#Starting development server at http://0.0.0.0:8000/
#Quit the server with CONTROL-C.
#Next, connect to the name or IP of the server (as defined in ALLOWED_HOSTS) on port 8000; for example, http://127.0.0.1:8000/. 
#You should be greeted with the NetBox home page. 
#Note that this built-in web service is for development and testing purposes only. It is not suited for production use.


