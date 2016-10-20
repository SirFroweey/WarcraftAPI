import requests
import json

API_KEY = "xmmsxkged3qz2urgnpn9vyc7x9mj2ucq"
ENDPOINT = "https://us.api.battle.net"
LOCALE = "en_US"

class InvalidHTTPCode(Exception):
	def __init__(self, request):
		self.request = request

	def __str__(self):
		return "{status} - {url} - {response}".format(
			status=self.request.status_code,
			url=self.request.url,
			response=self.request.text
		)

class Realm(object):
	"""
	Stores temporary server information
	"""
	def __init__(self):
		self.status = None
		self.battlegroup = None
		self.name = None
		self.locale = None
		self.queue = None
		self.connected_realms = None
		self.timezone = None
		self.type = None
		self.slug = None
		self.population = None

	def build_from(self, dict_object):
		for key, value in dict_object.iteritems():
			setattr(self, key, value)

	def __str__(self):
		return "<{name}:{status}>".format(
			name=self.name,
			status="Online" if self.status else "Offline"
		)

	def __repr__(self):
		return self.__str__()

class BattleNet:
	"""
	us.battle.net api interface
	"""
	def __init__(self):
		self._session = requests.Session()
		self._session.trust_env = False
		self.servers = {}

	def _generate_complete_url(self, resource, data=""):
		return "{endpoint}{resource}{data}?locale={locale}&apikey={api_key}".format(
			endpoint=ENDPOINT,
			resource=resource,
			data=data,
			locale=LOCALE,
			api_key=API_KEY
		)

	def _submit_request(self, complete_url):
		request = self._session.get(complete_url)
		if request.status_code == 200:
			return json.loads(request.text)
		raise InvalidHTTPCode(request)

	def find_realm(self, realm_name):
		if len(self.servers.keys()) > 0:
			for server_name, instance in sorted(self.servers.iteritems()):
				if str(server_name) == str(realm_name):
					return instance
			return None
		else:
			self.get_realms()
			return self.find_realm(realm_name)

	def link_connected_realms(self, realm_instance):
		"""
		Replace connected_realms strings with Realm() instances
		"""
		for realm_name in realm_instance.connected_realms:
			server_object = self.find_realm(realm_name)
			if server_object:
				realm_instance.connected_realms[realm_name] = server_object

	def get_realms(self, resource="/wow/realm/status"):
		if len(self.servers.keys()) > 0:
			self.servers = {}

		complete_url = self._generate_complete_url(resource)
		json_response = self._submit_request(complete_url)
		for server in json_response['realms']:
			server_object = Realm()
			server_object.build_from(server)
			self.servers[server_object.name] = server_object

if __name__ == "__main__":
	client = BattleNet()
	sample_realm = client.find_realm("Tichondrius")
	print client.servers
	print sample_realm
	print "complete"
