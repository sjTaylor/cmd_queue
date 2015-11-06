class Config:
	def __init__(self):
		self.server_ip   = 'localhost'
		self.server_port = 12345
		self.target_working_directory = '.'
		self.wd_is_list = False
		#timeout is in seconds
		self.cmd_timeout = 10
		self.log_file = 'log.txt'
		self.cmd_file = 'commands.txt'
		#will be prepended to log names
		self.output_prefix = './output_logs/'
		self.padding = 6

	def get_args(self,args):
		if len(args) % 2 != 1:
			raise RuntimeError("Bad Number of Arguments")
		for x in range(1,len(args),2):
			a = args[x]
			b = args[x+1]
			if a == '-ip':
				self.server_ip = b
			elif a == '-wd':
				self.target_working_directory = b
			elif a == '-c':
				self.cmd_file = b
			elif a == '-p':
				self.server_port = int(b)
			elif a == '-t':
				self.cmd_timeout = float(b)
			elif a == '-l':
				self.log_file = b
			elif a == '-o':
				self.output_folder = b
			else:
				raise RuntimeError("Bad Argument")
