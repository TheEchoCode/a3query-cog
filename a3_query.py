import discord
from discord.ext import commands
import a2s

EMOJI_FAIL = '\U0000274C'
EMOJI_WAIT = '\U000023F3'
EMOJI_CONN = '\U0001F4F6'
EMOJI_WARN = '\U000026A0'

class QueryResponse:
	"""An object to store the response data of the queries."""
	def __init__(self, info, users):
		"""Sets the attributes of the QueryResponse from the data provided from the a2s query.  
			info: The info of the server itself.  
			users: The info about the players."""
		try:
			self.server_name = info.server_name
			self.map = info.map_name
			self.mission = info.game
			self.server_type = self.get_type(info.server_type)
			self.password_protected = info.password_protected
			self.server_version = info.version
			self.server_type = self.get_type(info.server_type)
			keywords = info.keywords.split(",")
			self.battleeye = self.get_battle_eye(keywords[0])
			self.required_version = self.get_required_version(keywords[1])
			self.server_state = self.get_server_state(keywords[3])
			self.required_same_mods = self.get_required_mod(keywords[5])
			self.game_type = self.get_game_type(keywords[9])
			self.players = self.get_players(users)
			self.player_count = info.player_count
			self.player_max = info.max_players
		except Exception as e:
			print(f"Error: {str(e)}")
			raise e

	def get_battle_eye(self, val):
		states = {"bf": False, "bt": True}
		return states[val]
	def get_required_version(self, val):
		return val.replace("r", "")
	def get_server_state(self, val):
		states = {"s0": "No server", "s1": "Selecting mission", "s2": "Editing mission", "s3": "Assigning Roles", "s4": "Sending mission", "s5": "Loading mission", "s6": "Briefing", "s7": "Playing", "s8": "Debriefing", "s9": "Mission aborted"}
		return states[val]
	def get_required_mod(self, val):
		states = {"mf": False, "mt": True}
		return states[val]
	def get_game_type(self, val):
		states = {"tapex": "Apex campaign", "tcoop": "coop", "tctf": "Capture the flag", "tcti": "Capture the island", "tdm": "Deathmatch", "tendgame": "Endgame", "tescape": "Escape", "tkoth": "KOTF", "tlastman": "Last man standing", "tpatrol": "Combat patrol", "trpg": "RPG", "tsandbox": "Sandbox", "tsc": "Sector control", "tsupport": "Support", "tsurvive": "Survival", "ttdm": "Team deathmatch", "tunknown": "Unknown", "tvanguar": "Vanguard", "twarlord": "Warlods", "tzeus": "Zeus"}
		return states[val]
	def get_type(self, server_type):
		states = {"d": "Dedicated", "l": "Local", "p": "proxy"}
		return states[server_type]
	def get_players(self, users):
		players = []
		for user in users:
			players.append(user.name)
		return players

class A3Query:
	"""An object to query the data from Arma 3 servers.""" 
	def __init__(self, server_ip, server_port=2303):
		"""Makes the object ready to query information  
			server_ip: The ip or CNAME of the server.  
			server_port: The port of the server, the default is arma 3 default query port."""
		self.address = (server_ip, server_port)
	
	def query(self):
		"""Queries data through a2s and returns a QueryResponse."""
		info = a2s.info(self.address)
		users = a2s.players(self.address)
		return QueryResponse(info, users)

class QueryCog(commands.Cog):
	"""A cog (extension) to query info from Arma 3 servers."""
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command()
	# TODO You need to change the default server value here
	async def a3q(self, ctx, server : str="Default IP/CNAME of your server", port : int=2303):
		"""An example of how a command could work, shows the default info."""

		# Adds a hourglass reaction to the message while it queries
		await ctx.message.add_reaction(EMOJI_WAIT)
		try:
			query = A3Query(server_ip=server, server_port=port).query()
			# Creates a embed with some of the info from the query
			embed = discord.Embed(title=f"{query.server_name}")
			embed.add_field(name="State", value=query.server_state, inline=False)
			embed.add_field(name="Mission", value=query.mission, inline=False)
			embed.add_field(name="Map", value=query.map, inline=False)
			embed.add_field(name="Players", value=f"{query.player_count}/{query.player_max}", inline=False)
			await ctx.send(embed=embed)
			# If you want to print the variables to console for every execution of the command uncomment
			# print(vars(query))
		except Exception as e:
			# If some part of the query fails, add a cross reaction to the message to indicate it fails
			if str(e) == "timed out":
				await ctx.message.add_reaction(EMOJI_CONN)
				await ctx.message.add_reaction(EMOJI_WARN)
			else:
				await ctx.message.add_reaction(EMOJI_FAIL)
				print(f"Error: {str(e)}")
				raise e
		finally:
			# removes hourglass reaction after the query is done
			await ctx.message.remove_reaction(EMOJI_WAIT, self.bot.user)

def setup(bot):
	bot.add_cog(QueryCog(bot))


