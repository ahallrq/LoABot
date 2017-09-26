import sys
import socket
import string
import sqlite3
from d import *
import random 
cdice=dice()
HOST="irc.snoonet.org"
PORT=6667
NICK="Chaos-Bot-rq"
IDENT="Chaos-Bot"
REALNAME="AB49K-Chaos-Bot"
DM="iownall555!iownall555@snoonet/guide/iownall555"
DMLog=DM.split("!")[0] #Allows the bot to PM dm information to the DM.
print("Loading bot: configured DM" + DMLog)
enemies=[]

def dbaccess(query):
	conn = sqlite3.connect("chaos.db")
	c = conn.cursor()
	c.execute(query)
	rows = c.fetchall()
	conn.commit()
	conn.close()
	if not rows:
		return 1

	return rows
	
def getplayer(data):
		data=data.split('!')
		data.pop()
		return data[0].replace(":", '')
	
def log(data):
	if """##alientor :""" in data:
		f=open("alientor-log.txt", "a")
		f.write(str(data))
		f.close()
	else:
		pass

readbuffer=""
s=socket.socket( )
s.connect((HOST, PORT))
s.send("NICK %s\r\n" % NICK)
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
cnt=0

def cmd_roll(src, dst, args):
	try:
		result=cdice.roll(int(args[0]))
		s.send("""PRIVMSG ##alientor :Result - %s\r\n""" % result)
	except Exception,e:print str(e)

def cmd_dice(src, dst, args):
	dice = args[0].split("d")

	if len(dice) < 1 or len(dice) > 2:
		return
	elif len(dice) == 1:
		s.send("""PRIVMSG ##alientor :Result - %s\r\n""" % cdice.roll(int(dice[0])))
	elif len(dice) == 2:
		if (int(dice[0]) < 1) or (int(dice[0]) > 20):
			s.send("""PRIVMSG ##alientor :Error: To many or too little dice.\r\n""")
			return
		r = cdice.i_roll(int(dice[0]), int(dice[1]))
		s.send("""PRIVMSG ##alientor :Result - %s\r\n""" % ", ".join(r))

def cmd_info(src, dst, args):
	player = src.split("!")[0]
	try:
		result=dbaccess("select Character_Name, Character_Health, Mana, Int_, Str_,Cha_,Con_, Dex_,Points from players where Player_Name = '%s' " % (player))
		s.send("PRIVMSG %s :%s: Health: %s, Mana: %s, Int: %s, Str: %s, Cha: %s, Con: %s, Dex: %s, Available character points: %s\r\n" % (player, result[0][0],result[0][1],result[0][2],result[0][3],result[0][4],result[0][5],result[0][6],result[0][7],result[0][8]))
	except Exception,e:print str(e)

def cmd_inventory(src, dst, args):
	player = src.split("!")[0]
	try:
		result=dbaccess("select Character_Name from players where Player_Name = '%s' and Dead = '0'" % (player))
		if result == 1:
			print("No character for %s" % player)
		else:
			character=result[0][0]
		result=dbaccess("select Item, Item_Level, Base_Damage, Base_Defence, Quantity from inventory where Player_Item_Belongs_to = '%s' and Quantity >= 1" % (character))
		ccode = { False:'4', # red
				  True:'6' } # purple
		r=True
		if result == 1:
			print("No items in inventory for %s" % character)
		else:
			inv=[]
			for item in result:
				r = not r
				inv.append("%s%s - Level: %s, Damage: %s, Defence: %s, Quantity: %s ; " % (ccode[r], item[0], item[1], item[2], item[3], item[4]))
			s.send("PRIVMSG %s :Inventory: %s\r\n" % (player, ''.join(inv)))
	except Exception,e:print str(e)

def cmd_additem(src, dst, args):
	player = src.split("!")[0]

	try:
		quantity=int(line[9])
	except:
		quantity=1
	try:
		result=dbaccess("select Character_Name from players where Player_Name = '%s' and Dead = '0'" % (args[0]))
		if result == 1:
			print("No items in inventory for %s" % args[0])
		else:
			character=result[0][0]
			print character
		
		try:	
			result=dbaccess("select Quantity from Inventory where Player_Item_Belongs_to='%s' and Item='%s'" % (character ,args[1]))
			if result == 1:
				raise ValueError('There is no entry for this object')
			else:
				oldquantity=int(result[0][0])
				result=dbaccess("update Inventory set Quantity ='%s' where Player_Item_Belongs_to='%s' and Item='%s'" % ((oldquantity+quantity), character ,args[1]))
				s.send("PRIVMSG %s : addinventory success\r\n" % DMLog)
				s.send("PRIVMSG %s : You've just had a new item added to your inventory!\r\n" % player)
		except:
			try:
				level=0
				attack=0
				defence=0
				if len(line)>7:
					level=args[2]
					attack=args[3]
					defence=args[4]
				result=dbaccess("insert into Inventory (Item, Player_Item_Belongs_to, Item_Level, Base_Damage, Base_Defence, Quantity) values ('%s','%s','%s','%s','%s','%s')" % (args[1], character ,level, attack, defence ,quantity))
				if result == 1:
					s.send("PRIVMSG %s : addinventory success\r\n" % DM)
					s.send("PRIVMSG %s : You've just had a new item added to your inventory!\r\n" % player)
				else:
					pass	
			except Exception,e:
				s.send("PRIVMSG %s : addinventory failed\r\n" % DM)
				print str(e)	
	except Exception,e:print str(e)

def cmd_takeitem(src, dst, args):
	player = src.split("!")[0]

	try:
		takequantity=int(args[1])
	except:
		takequantity=1
	try:
		result=dbaccess("select Character_Name from players where Player_Name = '%s' and Dead = '0'" % (player))
		if result == 1:
			print("No items in inventory for %s" % player)
		else:
			character=result[0][0]
			print character
		try:
			result=dbaccess("select Quantity from Inventory where Player_Item_Belongs_to='%s' and Item='%s'" % (character ,args[0]))
			if result == 1:
				s.send("PRIVMSG %s : Invalid Item\r\n" % DMLog)
			else:
				quantity=int(result[0][0])
			result=dbaccess("update Inventory set Quantity ='%s' where Player_Item_Belongs_to='%s' and Item='%s'" % ((quantity-takequantity), character ,args[0]))
			
		except Exception,e:
			s.send("PRIVMSG %s : takeinventory failed\r\n" % DM)
			print str(e)	
		if result == 1:
			s.send("PRIVMSG %s : takeinventory success\r\n" % DM)
			s.send("PRIVMSG %s : You've just had an item removed from your inventory!\r\n" % player)
		else:
			pass				
	except Exception,e:print str(e)

def cmd_addattrpoint(src, dst, args):
	player = src.split("!")[0]

	try:
		result=dbaccess("select Points from players where Player_Name = '%s' and Dead = '0'" % (player))
		currentpoints=int(result[0][0])
		result=dbaccess("update players set Points ='%s' where Player_Name='%s' and Dead = '0'" % (currentpoints+1, player))
		s.send("PRIVMSG %s : Added Skill Point for %s\r\n" % (DM, player))
		s.send("PRIVMSG %s : Congratulation! You have just levelled up!\r\n" % player)			
	except Exception,e:print str(e)

def cmd_damage(src, dst, args):
	player = src.split("!")[0]

	try:
		result=dbaccess("select Character_Health from players where Player_Name = '%s' and Dead = '0'" % (player))
		currenthealth=int(result[0][0])
		result=dbaccess("update players set Character_Health ='%s' where Player_Name='%s' and Dead = '0'" % ((currenthealth-int(args[0])), player))
		s.send("PRIVMSG %s :%s has been damaged for %s points\r\n" % (DM, player, args[0]))
		s.send("PRIVMSG %s :oh no! You have taken %s points of damage!\r\n" % (player, args[0]))			
	except Exception,e:print str(e)	

def cmd_addattr(src, dst, args):
	skills = {
		"int": "Int_",
		"str": "Str_",
		"dex": "Dex_",
		"con": "Con_",
		"cha": "Cha_"
	}

	player = src.split("!")[0]

	result=dbaccess("select Points from players where Player_Name = '%s' and Dead = '0'" % (player))
	if result == 1:
		s.send("PRIVMSG %s : You have to specify an attribute to increase! (%s)\r\n" % (player, ", ".join(skills.keys())))
	else:
		currentpoints=int(result[0][0])
		if currentpoints<1:
			s.send("PRIVMSG %s : You don't have enough attr points!\r\n" % player)	
		else:
			try:
				skill = args[0]
				if skill not in skills:
					s.send("PRIVMSG %s :Please pick a valid attribute! (int, dex, str, con)\r\n" % player)	
				try:
					result=dbaccess("update players set Points ='%s' where Player_Name='%s' and Dead = '0'" % (currentpoints-1, player))
					result=dbaccess("select %s from players where Player_Name = '%s' and Dead = '0'" % (skill, player))
					skill_level=int(result[0][0])
					result=dbaccess("update players set %s ='%s' where Player_Name='%s' and Dead = '0'" % (skill, skill_level+1, player))
					s.send("PRIVMSG %s : %s Just spend a skill point \r\n" % (DM, player))
					s.send("PRIVMSG %s :Congratulations! You have spent your Attribute point!\r\n" % player)			
				except Exception,e:print str(e)	
	
			except:
				s.send("PRIVMSG %s : You have to specify an attribute to increase! (%s)\r\n" % (player, ", ".join(skills.keys())))

def cmd_moveitem(src, dst, args):
	try:
		result=dbaccess("select Character_Name from players where Player_Name = '%s' and Dead = '0'" % (args[0]))
		if result == 1:
			print("No items in inventory for %s" % args[0])
		else:
			character1=result[0][0]
			print character1
			
		result=dbaccess("select Character_Name from players where Player_Name = '%s' and Dead = '0'" % (args[1]))
		if result == 1:
			print("No items in inventory for %s" % args[1])
		else:
			character2=result[0][0]
			print character2		
			
			
		try:
			result=dbaccess("select Quantity from Inventory where Player_Item_Belongs_to='%s' and Item='%s'" % (character1 ,args[2]))
			if result == 1:
				s.send("PRIVMSG %s : Invalid Item\r\n" % DMLog)
			else:
				quantity=int(result[0][0])
			result=dbaccess("update Inventory set Player_Item_Belongs_to ='%s' where Player_Item_Belongs_to='%s' and Item='%s'" % (character2, character1 ,args[2]))
			
		except Exception,e:
			s.send("PRIVMSG %s : Moving %s from %s to %s -- FAILED\r\n" % ( DMLog, args[2], character1, character2))
			print str(e)	
		if result == 1:
			s.send("PRIVMSG %s : Moved %s from %s to %s\r\n" % (DMLog, args[2], character1, character2))
			s.send("PRIVMSG %s : You've just had an item added from your inventory!\r\n" % character2)
		else:
			pass				
	except Exception,e:print str(e)

def cmd_addenemy(src, dst, args):
	try:
		stats = [0, 0, 0, 0, 0] # [int, dex, str, con, cha] in that order
		enemylevel=int(args[1])
		enemyhealth=enemylevel*random.randint(5,10)
		for i in range(0, enemylevel):
			stats[random.randint(0,4)] += 1
		mainattack=random.randint(1,3)
		enemies.append([args[0], enemylevel, enemyhealth, stats[0], stats[1], stats[2], stats[3], stats[4],mainattack,1])
		s.send("""PRIVMSG ##alientor : A level %s enemy %s with %s health has spotted you!\r\n""" % (enemylevel, args[0], enemyhealth))
	except Exception,e:print str(e)

def cmd_hitenemy(src, dst, args):
	try:
		for enemy in enemies:
			if args[0] == enemy[0]:
				if enemy[9]==0:
					pass
				else:
					if len(enemy)>10:
						enemyhealth=enemy.pop()
					else:
						enemyhealth=enemy[2]
					enemyhealth=(enemyhealth-int(args[1]))
					enemy.append(enemyhealth)
					if enemyhealth<1:
						s.send("""PRIVMSG ##alientor :You have killed %s!!!!\r\n""" % enemy[0])
					else:
						s.send("""PRIVMSG ##alientor :You have hit %s for %s points!\r\n""" % (enemy[0], (int(args[1])-enemy[6])))
	except Exception,e:print str(e)

def cmd_enemyattack(src, dst, args):
	try:
		for enemy in enemies:
			if args[0] == enemy[0]:
				if enemy[9]==0:
					pass
				else:
					roll=cdice.roll(20)
					if roll > 12:
						s.send("""PRIVMSG ##alientor :%s Missed!!!\r\n""" % (enemy[0]))
					else:
						roll=cdice.roll(int(line[5]))
						if enemy[8]==1:
							damage=roll+enemy[3]
						if enemy[8]==2:
							damage=roll+enemy[4]
						if enemy[8]==3:
							damage=roll+enemy[5]
						s.send("""PRIVMSG ##alientor :%s hits for %s!!!\r\n""" % (enemy[0], damage))
	except Exception,e:print str(e)

def cmd_addnewcharacter(src, dst, args):
	try:
		m=cdice.roll(20)
		if m > 17:
			ismagic=1
		else:
			ismagic=0
		newplayer=args[0]
		newcharacter=args[1]
		level=args[2]
		
		result=dbaccess("""insert into players (Player_Name, Character_Name, Character_Health, Int_, Str_, Cha_, Con_, Dex_, Gold, Magic, Mana, Points, Dead)
						values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % (newplayer, newcharacter, 100, 0,0,0,0,0,0,0,ismagic,level,0))
		dbaccess("insert into Inventory (Item, Player_Item_Belongs_to, Item_Level, Base_Damage, Base_Defence, Quantity) values ('basic_clothes','%s','%s','%s','%s','%s')" % (newplayer, 1 ,0, 0 ,1))

		if result == 1:
			s.send("PRIVMSG %s : Added a new player!\r\n" % DM)
			s.send("PRIVMSG %s : You've just been given a new character! Please use !info, !inventory and !addattr to level up - All commands can be PM'd to the bot to keep the channel uncluttered\r\n" % newplayer)		
			if ismagic==1:
				s.send("PRIVMSG %s : Lucky you! You have been born with the rare gift of natural magic! This means you can use magic without needing to learn any spells! you can only level up your magic by casting spells and rolling a nat 20.\r\n" % newplayer)
	except Exception,e:print str(e)

bot_commands = {
	"roll" : {"func": cmd_roll, "needs-dm": True},
	"dice" : {"func": cmd_dice, "needs-dm": True},
	"info" : {"func": cmd_info, "needs-dm": False},
	"inventory" : {"func": cmd_inventory, "needs-dm": False},
	"additem" : {"func": cmd_additem, "needs-dm": True},
	"takeitem" : {"func": cmd_takeitem, "needs-dm": True},
	"addattrpoint" : {"func": cmd_addattrpoint, "needs-dm": True},
	"damage" : {"func": cmd_damage, "needs-dm": True},
	"addattr" : {"func": cmd_addattr, "needs-dm": False},
	"moveitem" : {"func": cmd_moveitem, "needs-dm": True},
	"addenemy" : {"func": cmd_addenemy, "needs-dm": True},
	"hitenemy" : {"func": cmd_hitenemy, "needs-dm": True},
	"enemyattack" : {"func": cmd_enemyattack, "needs-dm": True},
	"addnewcharacter" : {"func": cmd_addnewcharacter, "needs-dm": True}
}

while 1:
	data = s.recv(1024)
	if data.find ('PING' ) != -1:
			command = data.split(" or /raw PONG ")
			command=command.pop()
			command=command.replace(' now.', '' )
			print "Received keepalive from server. Responding..."
			s.send ( 'PONG %s\r\n' % command.rstrip())
	readbuffer=readbuffer+data
	temp=string.split(readbuffer, "\n")
	readbuffer=temp.pop( )

	for line in temp:
		line=string.rstrip(line)
	
	if ":Global!Global@snoonet/services/Global" in line:
		s.send("""JOIN :##alientor\r\n""")
	line=string.split(line)

	if not line[0].startswith(":"): continue
	msg_src = line[0][1:]
	msg_type = line[1]
	msg_dst = line[2]
	msg_line = line[3:]
	if len(msg_line) > 0:
		msg_line[0] = msg_line[0][1:]

	print "[%s] %s --> %s: %s" % (msg_type, msg_src, msg_dst, " ".join(msg_line))

	if msg_type != "PRIVMSG": continue
	elif msg_line[0].startswith("!"):
		if msg_line[0][1:] in bot_commands:
			if len(msg_line) == 1: args = []
			else: args = msg_line[1:]
			print("%s sent command \"%s\" to %s" % (msg_src, " ".join(msg_line), msg_dst))

			cmd = bot_commands[msg_line[0][1:]]
			if cmd["needs-dm"] and msg_src != DM:
				s.send("""NOTICE %s :Access denied.\r\n""" % (msg_src.split("!")[0]))
			elif cmd["func"] != None:
				cmd["func"](msg_src, msg_dst, args)
