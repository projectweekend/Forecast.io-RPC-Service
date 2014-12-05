from StringIO import StringIO

from fabric import api
from fabric.contrib.files import exists


UPSTART_TEMPLATE = """
description "Forecast.io-RPC-Service"
start on runlevel [2345]
stop on runlevel [06]
respawn
respawn limit 10 5

env LOGGLY_TOKEN={loggly_token}
env LOGGLY_SUBDOMAIN={loggly_domain}
env RABBIT_URL={rabbit_url}
env FORECAST_KEY={forecast_key}

script
        cd {home_directory}/Forecast.io-RPC-Service/app && node main.js
end script
"""


def local():
	api.env.hosts = ['{0}.local'.format(api.prompt('Hostname:'))]
	api.env.user = api.prompt('User:')


def install():
	api.require('hosts', provided_by=[local])

	if exists('/etc/init/forecast-rpc.conf', use_sudo=True):
		print('"forecast-rpc" is already installed, use the "update" task for changes')
		return

	upstart_values = {}
	upstart_values['home_directory'] = '/home/{0}'.format(api.env.user)
	upstart_values['loggly_token'] = api.prompt("Loggly token:")
	upstart_values['loggly_domain'] = api.prompt("Loggly domain:")
	upstart_values['forecast_key'] = api.prompt("Forecast.io key:")
	upstart_values['rabbit_url'] = api.prompt("Rabbit URL:")
	upstart_file = StringIO(UPSTART_TEMPLATE.format(**upstart_values))

	with api.cd('/etc/init'):
		upload = api.put(upstart_file, 'forecast-rpc.conf', use_sudo=True)
		assert upload.succeeded

	api.run('git clone https://github.com/projectweekend/Forecast.io-RPC-Service.git')

	with api.cd('~/Forecast.io-RPC-Service/app'):
		api.run('npm install')

	api.sudo('service forecast-rpc start')


def update():
	api.require('hosts', provided_by=[local])

	with api.settings(warn_only=True):
		api.sudo('service forecast-rpc stop')

	with api.cd('~/Forecast.io-RPC-Service'):
		api.run('git pull origin master')

	with api.cd('~/Forecast.io-RPC-Service/app'):
		api.run('npm install')

	api.sudo('service forecast-rpc start')
