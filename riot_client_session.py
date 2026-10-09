from urllib3.exceptions import InsecureRequestWarning
from requests import Session, Response
from urllib3 import disable_warnings
from base64 import b64encode
from re import findall
from json import load
from os import path

disable_warnings(InsecureRequestWarning)

class RiotClient:
	def __init__(self) -> None:
		with open("config.json") as cfg:
			config_file = load(cfg)

		self.session: Session = Session()

		self.lockfile_path: str = config_file['file_path']['lockfile']
		self.shootergame_path: str = config_file['file_path']['shootergame']
		self.riot_client_services_path: str = config_file['file_path']['riot_client_services']
		self.lockfile_content: dict = self.fetch_lockfile_content()

		self.lockfile_headers: dict = {
			"Authorization": f"Basic {self.lockfile_content['token']}"
		}

		self.last_match_id: str = ""
		self.player_information: dict = {}
		self.puuid: str = self.fetch_puuid()
		self.region, self.shard = self.fetch_region_and_shard()

	def fetch_lockfile_content(self) -> dict:
		try:
			with open(path.expanduser(self.lockfile_path), "r", errors="ignore") as lockfile:

				lockfile_content = lockfile.read().strip()
				lockfile_content = lockfile_content.split(":")
				
				lockfile_dict: dict = {
					"name": lockfile_content[0],
					"pid": lockfile_content[1],
					"port": lockfile_content[2],
					"token": b64encode(f"riot:{lockfile_content[3]}".encode()).decode(),
					"protocol": lockfile_content[4]
				}
			return lockfile_dict

		except:
			pass

		return {}

	def fetch_version(self) -> str:
		try:
			response = self.session.get(
				f"{self.lockfile_content['protocol']}://127.0.0.1:{self.lockfile_content['port']}/product-session/v1/external-sessions",
				headers=self.lockfile_headers,
				verify=False
			)
			
			for key, value in response.json().items():
				if key != "host_app" and isinstance(value, dict) and value.get("productId") == "valorant":
					return value.get("version", "")

		except:
			pass
		
		return None

	def fetch_entitlements_and_auth(self) -> dict:
		try:
			response = self.session.get(
				f"{self.lockfile_content['protocol']}://127.0.0.1:{self.lockfile_content['port']}/entitlements/v1/token",
				headers=self.lockfile_headers,
				verify=False
			)
			headers: dict = {
				"X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
				"X-Riot-ClientVersion": self.fetch_version(),
				"X-Riot-Entitlements-JWT": response.json()['token'],
				"Authorization": f"Bearer {response.json()['accessToken']}"
			}
			return headers

		except:
			pass
		
		return {}

	def fetch_region_and_shard(self) -> dict:
		try:
			with open(self.shootergame_path, "r", errors="ignore") as file:
				shootergame_content = file.read()

			matches = findall(r"https://glz-(.+?)-1.(.+?).a.pvp.net", shootergame_content)
			region, shard = matches[-1]
			return region, shard
		
		except:
			pass
		
		return {}

	def fetch_puuid(self) -> str:
		try:
			response = self.session.get(f"{self.lockfile_content['protocol']}://127.0.0.1:{self.lockfile_content['port']}/chat/v1/session",
				headers=self.lockfile_headers,
				verify=False
			)
			print(f"Logged in as: {response.json()['puuid']}")
			return response.json()['puuid']

		except:
			pass
		
		return None
