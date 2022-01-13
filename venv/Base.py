from Config import *
#global config
class BaseSpec(Config):
	config = Config()
	def loadSysLogServers(self):
		print("loading DNOR users ...i am in Base spec class")

	def loadconfig(self):
		print("loadconfig from basespec")

	def __init__(self):
		self.loadSysLogServers()
		#self.config = Config()

