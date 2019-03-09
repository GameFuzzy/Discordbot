import discord
import asyncio
import logging
import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

logging.basicConfig(level=logging.INFO)

client = discord.Client()
@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')
	
	mentionMessages = []
	botActivity = discord.Activity(name=os.environ['activityName'],type=discord.ActivityType.watching)
	await client.change_presence(activity = botActivity)
	await client.user.edit(username="Bot Mcbotface")

	
# I DON'T KNOW

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	print(f"Message sent by {message.author}")
	if message.content.startswith("<@") and len(message.content.split()) == 3:
		print("Mention found")
		print(message.content.split())
		print(len(message.content.split()))
		mention,wordis,epicword = message.content.split()
		if wordis == "is" and epicword == "epic":
			print("is epic")
			with open("botdatabase","r") as db:
				dbLines = db.readlines()
			namefound = False
			dbNewLines = []
			for line in dbLines:
				userElements = line.split('=')
				if userElements[0] == mention:
					print("ID found")
					timeform = "times"
					userElements[1] = str(int(userElements[1]) + 1)
					print("Epiccounter = " + userElements[1])
					epiccount = userElements[1] 
					namefound = True
					print("Modified line:" + userElements[0] + "=" + userElements[1])
					if len(userElements) == 2:
						dbNewLines.append(f"{userElements[0]}={userElements[1]}\n")
					break
				print(userElements[0] + "=" + userElements[1] + "not matching")
				if len(userElements) == 2:
					dbNewLines.append(f"{userElements[0]}={userElements[1]}")
			if namefound == True:
				with open("botdatabase","w") as dbw:
					dbw.writelines(dbNewLines)
			else:
				with open("botdatabase","a") as dba:
					dba.write(f"{mention}=1" + "\n")
				epiccount = 1
				timeform = "time"
			if int(epiccount) < 5:
				epicLikeliness = "are probably not epic"
			elif int(epiccount) < 10:
				epicLikeliness = "might be epic"
			elif int(epiccount) < 20:
				epicLikeliness = "are likely epic"
			elif int(epiccount) < 30:
				epicLikeliness = "are very likely epic"
			elif int(epiccount) < 50:
				epicLikeliness = "are epic"
			await message.channel.send(f'{mention} has now been called epic {epiccount} {timeform}\n They {epicLikeliness}')

# NEW MEMBER REACTION ROLES

@client.event
async def on_raw_reaction_add(payload):  # Will be dispatched every time a user adds a reaction to a message the bot can see
	role = ""
	badBool = False
	inviterBool = False
	
	print("Reaction added")
	if not payload.guild_id:
		# In this case, the reaction was added in a DM channel with the bot
		print("Dafuq")
		return
	
	guild = client.get_guild(payload.guild_id)  # You need the guild to get the member who reacted
	member = guild.get_member(payload.user_id)  # Now you have the key part, the member who should receive the role
	
	if payload.message_id != int(os.environ['messageID']):
		print(os.environ['messageID'])
		print(payload.message_id)
		print("Not role reaction")
		
		conn = psycopg2.connect(DATABASE_URL, sslmode='require')
		
		try:
			cur = conn.cursor()
			cur.execute("SELECT * FROM mentionMessageTable WHERE id=%s", (str(payload.message_id),))
			mentionMessage = cur.fetchone()
			for memberRole in member.roles:
				if memberRole.id == int(os.environ['inviterRoleID']):
					inviterBool = True
					break
			if mentionMessage[0] == payload.message_id and str(payload.emoji) == str(os.environ['emojiIDInviter']) and inviterBool:
				cur.execute("DELETE FROM mentionMessageTable WHERE id=%s;", (str(payload.message_id),))
				conn.commit()
				welcomeChannel = client.get_channel(int(os.environ['welcomeChannelID']))
				print("Message ID matches inviter ping message id, sending welcome message...")
				await welcomeChannel.send("Welcome " + "<@" + mentionMessage[1] + ">" + "!" + os.environ['welcomeMessage'])
			cur.close()
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
		finally:
			if conn is not None:
				conn.close()
		return
		
	print("Reaction added to message")
	
	if str(payload.emoji) == str(os.environ['emojiIDMember']):  # payload.emoji is a PartialEmoji. You have different possibilities to check for a proper reaction
		print("Emoji matches")
		role = guild.get_role(int(os.environ['roleIDMember'])) # You also need the role
		messageChannel = client.get_channel(int(os.environ['inviterChannelID']))
		mentionMessageDab = await messageChannel.send(os.environ['inviterPingMessage'] + " please invite " + member.nick)
		try:
			conn = psycopg2.connect(DATABASE_URL, sslmode='require')
			cur = conn.cursor()
			cur.execute("INSERT INTO mentionMessageTable VALUES (%s, %s);", (str(mentionMessageDab.id), str(payload.user_id)))
			conn.commit()
			cur.close()
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
		finally:
			if conn is not None:
				conn.close()
 
		print("Sent message")
	# Gotta do same thing for friends
	elif str(payload.emoji) == str(os.environ['emojiIDFriend']):
		role = guild.get_role(int(os.environ['roleIDFriend']))
	else:
		# An improper emoji has been used to react to the message
		print("Wrong emoji")
		print(os.environ['emojiIDFriend'])
		print(os.environ['emojiIDMember'])
		print(payload.emoji)
		badBool = True
	
	reactionChannel = client.get_channel(payload.channel_id)
	reactionMessage = await reactionChannel.get_message(payload.message_id)
	await reactionMessage.remove_reaction(payload.emoji, member)
	if badBool == False:
		await member.add_roles(role, reason='Invited to clan')  # Finally add the role to the member
		print("Added role")
client.run(os.environ['discordToken'])
