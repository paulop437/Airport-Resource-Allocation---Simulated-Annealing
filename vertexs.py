import json

class Vertex:
	def __init__(self,name:str, destination, cost):
		self.name = name
		self.destination = destination
		self.cost = cost

	def __str__(self):
		return "Name: " + self.name

	def get_name(self):
		return self.name
