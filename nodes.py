import json

class Node:
	def __init__(self,name:str, parent, path_cost:int):
		self.name = name
		self.parent = parent
		self.path_cost = path_cost
		if parent != None:
			self.total_cost = self.path_cost + self.parent.get_total_cost()
		else:
			self.total_cost = path_cost
			
	def get_total_cost(self):
		return self.total_cost

	def get_path_cost(self):
		return self.path_cost

	def get_parent(self):
		return self.parent
	
	def get_name(self):
		return self.name
	



