import yaml
from yaml.loader import SafeLoader

with open('data.yaml', 'r') as file:
    config = yaml.load(file, Loader = SafeLoader)

host_config = config['host']
user_config = config['user']
password_config = config['password']
database_config = config['database']