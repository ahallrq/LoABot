from random import randint

class dice:
	def roll(self, d):
		result=[]
		for i in range(1,1000):
			result.append(randint(1,d))
		return result[randint(0,999)]

	def i_roll(self, dice, sides):
		results = []
		for i in range(dice):
			results.append(str(randint(1, sides)))
		return results