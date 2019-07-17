import asyncio
import datetime
import logging
import os

import discord
import psycopg2
from discord.ext import commands
from mcrcon import MCRcon

DATABASE_URL = os.environ['DATABASE_URL']

logging.basicConfig(level=logging.INFO)

testing = False

client = commands.Bot(command_prefix="?")

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    botActivity = discord.Activity(name=os.environ['activityName'], type=discord.ActivityType.watching)
    await client.change_presence(activity=botActivity)
    # await client.user.edit(username="Cephalon Lobby") #This can be used to change the bot username
    print(next_weekday(datetime.datetime.utcnow(), 1))
    client.loop.create_task(run_at(next_weekday(datetime.datetime.utcnow(), 1), addColumn()))
    # For testing
    # client.loop.create_task(run_at(datetime.datetime(2019, 4, 7, 12, 52), addColumn()))


async def wait_for(dt):
    # sleep until the specified datetime
    while True:
        now = datetime.datetime.utcnow()
        remaining = (dt.replace(hour=12, minute=0) - now).total_seconds()
        if remaining < 86400:
            break
        # asyncio.sleep doesn't like long sleeps, so don't sleep more
        # than a day at a time
        await asyncio.sleep(86400)
    await asyncio.sleep(remaining)


async def run_at(dt, coro):
    await client.wait_until_ready()
    await wait_for(dt)
    return await coro


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


async def addColumn():
    while True:
        messageChannel = client.get_channel(int(os.environ['staffChannelID']))
        await messageChannel.send(os.environ['adminPing'] + " Time for the weekly member check Gears!")
        # DanisDGK add a new column to the spreadsheet here. You can use datetime.date.utcnow() for the date if you need that in the top column.
        await wait_for(next_weekday(datetime.datetime.utcnow(), 1))


@client.command()
async def joinMinecraft(ctx, username):
    with MCRcon("MCRCON_IP", os.environ['MCRCON Pass']) as mcr:
        resp = mcr.command("/whitelist add " + username)
        print(resp)

@client.command()
async def testingmode(ctx):
    global testing
    if testing:
        testing = False
        await ctx.send("Testing mode deactivated")
    else:
        testing = True
        await ctx.send("Testing mode activated")
async def is_staff(ctx):
    for permissionRole in ctx.author.roles:
        if permissionRole.id == int(os.environ['roleIDOfficer']) or permissionRole.id == int(
                os.environ['roleIDLeader']):
            return True


def nickOrName(dabbermember):
    if dabbermember.nick is not None:
        return dabbermember.nick
    else:
        return dabbermember.name


async def deleteErrorMessage(dabErrorMessage):
    await asyncio.sleep(30)
    await dabErrorMessage.delete()


@client.command()
@commands.check(is_staff)
async def fixGhostWolfsName(ctx):
    GhostWolf = ctx.guild.get_member(146356716894814209)
    await GhostWolf.edit(nick="👑 GhostWolf")

@client.command()
@commands.check(is_staff)
async def inactive(ctx, *inactiveMembers):
    bigOOF = False
    for epicdabmember in ctx.guild.members:
        for role in epicdabmember.roles:
            if role.id is not int(os.environ['roleIDLeader']):
                bigOOF = True
        if bigOOF:
            for inactiveMember in inactiveMembers:
                if epicdabmember.mention == inactiveMember:
                    for dabRole in epicdabmember.roles:
                        if dabRole is not ctx.guild.default_role:
                            await epicdabmember.remove_roles(dabRole, reason="Inactivity")
                    await epicdabmember.add_roles(ctx.guild.get_role(int(os.environ['roleIDFriend'])),
                                                  ctx.guild.get_role(
                                                      int(os.environ['tennoSeparator'])),
                                                  ctx.guild.get_role(
                                                      int(os.environ['roleIDSeparator'])),
                                                  reason="Inactivity")
                    await epicdabmember.edit(
                                nick=os.environ['emojiIDFriend'] + " " + nickOrName(epicdabmember).replace(" ",
                                                                                                        "").replace(
                                    os.environ['emojiIDStaff'],
                                    "").replace(
                                    os.environ['emojiIDMember'],
                                    "").replace(
                                    os.environ['emojiIDMember'],
                                    ""))

@client.command()
@commands.check(is_staff)
async def nicknameemojis(ctx):
    statusMessage = await ctx.channel.send("Changing nickname emojis...")
    for dabbymember in ctx.guild.members:
        global emojiRoleFound
        emojiRoleFound = False
        if dabbymember is not ctx.guild.owner:
            for emojiRole in dabbymember.roles:
                if emojiRole.id == int(os.environ['roleIDLeader']):
                    emojiRoleFound = True
                    break

            if not emojiRoleFound:
                for emojiRole in dabbymember.roles:
                    if emojiRole.id == int(os.environ['roleIDOfficer']):

                        emojiRoleFound = True
                        if (os.environ['emojiIDStaff'] in nickOrName(dabbymember)):
                            await dabbymember.edit(
                                nick=os.environ['emojiIDStaff'] + " " + nickOrName(dabbymember).replace(" ",
                                                                                                        "").replace(
                                    os.environ['emojiIDStaff'],
                                    ""))
                        elif os.environ['emojiIDFriend'] in nickOrName(dabbymember):
                            await dabbymember.edit(
                                nick=os.environ['emojiIDStaff'] + " " + nickOrName(dabbymember).replace(" ",
                                                                                                        "").replace(
                                    os.environ['emojiIDFriend'],
                                    ""))
                        elif os.environ['emojiIDMember'] in nickOrName(dabbymember):
                            await dabbymember.edit(
                                nick=os.environ['emojiIDStaff'] + " " + nickOrName(dabbymember).replace(" ",
                                                                                                        "").replace(
                                    os.environ['emojiIDMember'],
                                    ""))
                        else:
                            emojiRoleFound = True
                            await dabbymember.edit(
                                nick=os.environ['emojiIDStaff'] + " " + nickOrName(dabbymember).replace(" ", ""))

            if not emojiRoleFound:
                for emojiRole in dabbymember.roles:
                    if emojiRole.id == int(os.environ['roleIDMember']):

                        emojiRoleFound = True
                        if (os.environ['emojiIDMember'] in nickOrName(dabbymember)):
                            await dabbymember.edit(
                                nick=os.environ['emojiIDMember'] + " " + nickOrName(dabbymember).replace(" ",
                                                                                                         "").replace(
                                    os.environ['emojiIDMember'],
                                    ""))
                        elif os.environ['emojiIDFriend'] in nickOrName(dabbymember):
                            await dabbymember.edit(
                                nick=os.environ['emojiIDMember'] + " " + nickOrName(dabbymember).replace(" ",
                                                                                                         "").replace(
                                    os.environ['emojiIDFriend'],
                                    ""))
                        elif os.environ['emojiIDStaff'] in nickOrName(dabbymember):
                            await dabbymember.edit(
                                nick=os.environ['emojiIDMember'] + " " + nickOrName(dabbymember).replace(" ",
                                                                                                         "").replace(
                                    os.environ['emojiIDStaff'],
                                    ""))
                        else:
                            emojiRoleFound = True
                            await dabbymember.edit(
                                nick=os.environ['emojiIDMember'] + " " + nickOrName(dabbymember).replace(" ", ""))

            if not emojiRoleFound:
                for emojiRole in dabbymember.roles:
                    if emojiRole.id == int(os.environ['roleIDFriend']):

                        emojiRoleFound = True
                        if (os.environ['emojiIDFriend'] in nickOrName(dabbymember)):
                            await dabbymember.edit(
                                nick=os.environ['emojiIDFriend'] + " " + nickOrName(dabbymember).replace(" ",
                                                                                                         "").replace(
                                    os.environ['emojiIDFriend'],
                                    ""))
                        elif os.environ['emojiIDMember'] in nickOrName(dabbymember):
                            await dabbymember.edit(
                                nick=os.environ['emojiIDFriend'] + " " + nickOrName(dabbymember).replace(" ",
                                                                                                         "").replace(
                                    os.environ['emojiIDMember'],
                                    ""))
                        elif os.environ['emojiIDStaff'] in nickOrName(dabbymember):
                            await dabbymember.edit(
                                nick=os.environ['emojiIDFriend'] + " " + nickOrName(dabbymember).replace(" ",
                                                                                                         "").replace(
                                    os.environ['emojiIDStaff'],
                                    ""))
                        else:
                            emojiRoleFound = True
                            await dabbymember.edit(
                                nick=os.environ['emojiIDFriend'] + " " + nickOrName(dabbymember).replace(" ", ""))
    await statusMessage.delete()
    await ctx.channel.send("Nickname emojis have been changed.")


@client.command()
@commands.check(is_staff)
async def spreadsheetmanualupdate(ctx):
    for dabMember in ctx.guild.members:
        epicMember = []
        # DanisDGK Replace this comment with a check for if nickOrName(dabMember) is already in name column of the spreadsheet with your spreadsheet magic. If it is just return.

        epicMember.insert(0, nickOrName(dabMember))

        if dabMember.top_role.id == int(os.environ['roleIDOfficer']):
            epicMember.insert(1, "Officer")

        elif dabMember.top_role.id == int(os.environ['roleIDMember']):
            epicMember.insert(1, "Member")

        elif dabMember.top_role.id == int(os.environ['roleIDFriend']):
            epicMember.insert(1, "Friend")

        else:
            epicMember.insert(1, "Nothing")
            print("Dafuq")

        # DanisDGK Insert epicMember[0] into the spreadsheet as the name and epicMember[1] as the role here.


@client.event
async def on_guild_channel_update(before, after):
    if before.category is not after.category:
        messageChannel = client.get_channel(int(os.environ['staffChannelID']))
        await messageChannel.send("It work a veri nice 👌")

@client.event
async def on_member_remove(member):
    messageChannel = client.get_channel(int(os.environ['staffChannelID']))
    memberAge = datetime.datetime.utcnow() - member.joined_at
    days = memberAge.days
    hours, remainder = divmod(memberAge.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    for memberCheckRole in member.roles:
        if memberCheckRole.id == int(os.environ['roleIDMember']):
            await messageChannel.send(
                os.environ['adminPing'] + """**
A member has left. **""" + """
Warframe IGN: """ + nickOrName(member) + """
""" + str(member) + " (" + str(member.id) + ") " + """
They had the roles: """ + (', '.join(nameRole.name for nameRole in member.roles[1:-1])) + ' and ' + member.roles[
                    -1].name + """.
""" + "They joined " + str(days) + " days, " + str(hours) + " hours and " + str(
                    minutes) + " minutes ago.")

            break

@client.event  # This event runs whenever a user updates: status, game playing, avatar, nickname or role
async def on_member_update(before, after):
    isStaff = False
    messageChannel = client.get_channel(int(os.environ['inviterChannelID']))

    if len(before.roles) < len(after.roles):
        new_role = next(role for role in after.roles if role not in before.roles)

        for role in after.roles:
            if role.id == int(os.environ['roleIDLeader']) or role.id == int(os.environ['roleIDOfficer']):
                isStaff = True
                break

        if new_role.id is not int(os.environ['roleIDLeader']) and new_role.id is not int(
                os.environ['roleIDOfficer']) and new_role and isStaff:
            return

        if new_role.id == int(os.environ['roleIDOfficer']):
            for role in after.roles:
                if role.id == int(os.environ['roleIDFriend']):
                    #DanisDGK Here, if possible, search for the member in the spreadsheet with the name returned by nickOrName(after) and change their rank to "Staff"
                    await after.remove_roles(role)
                    await after.edit(
                        nick=os.environ['emojiIDStaff'] + " " + nickOrName(after).replace(" ", "").replace(
                            os.environ['emojiIDFriend'],
                            ""))
                    return

                elif role.id == int(os.environ['roleIDMember']):
                    await after.edit(
                        nick=os.environ['emojiIDStaff'] + " " + nickOrName(after).replace(" ", "").replace(
                            os.environ['emojiIDMember'],
                            ""))
                    return

        if new_role.id == int(os.environ['roleIDMember']):
            for role in after.roles:
                if role.id == int(os.environ['roleIDFriend']):
                    #DanisDGK Here, if possible, search for the member in the spreadsheet with the name returned by nickOrName(after) and change their rank to "Member"

                    await after.remove_roles(role)
                    await after.edit(
                        nick=os.environ['emojiIDMember'] + " " + nickOrName(after).replace(" ", "").replace(
                            os.environ['emojiIDFriend'],
                            ""))

                    mentionMessageDab = await messageChannel.send(
                        os.environ['inviterPingMessage'] + " and " + os.environ[

                            'recruiterPingMessage'] + " please invite " + after.nick + " to the clan.")
                    await mentionMessageDab.add_reaction(
                        os.environ['emojiIDInviter'])
                    try:
                        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
                        cur = conn.cursor()
                        cur.execute("INSERT INTO mentionMessageTable VALUES (%s, %s, True);",
                                    (str(mentionMessageDab.id), str(after.id)))
                        conn.commit()
                        cur.close()
                    except (Exception, psycopg2.DatabaseError) as error:
                        print(error)
                    finally:
                        if conn is not None:
                            conn.close()
                    return

        if new_role.id == int(os.environ['roleIDFriend']):
            for role in after.roles:
                if role.id == int(os.environ['roleIDMember']):
                    #DanisDGK Here, if possible, search for the member in the spreadsheet with the name returned by nickOrName(after) and change their rank to "Friend"
                    await after.remove_roles(role)
                    await after.edit(
                        nick=os.environ['emojiIDFriend'] + " " + nickOrName(after).replace(" ", "").replace(
                            os.environ['emojiIDMember'],
                            ""))
                    return

# NEW MEMBER REACTION ROLES

@client.event
async def on_raw_reaction_add(
        payload):  # Will be dispatched every time a user adds a reaction to a message the bot can see
    role = ""
    badBool = False
    inviterBool = False
    global testing

    print("Reaction added")
    if not payload.guild_id:
        # In this case, the reaction was added in a DM channel with the bot
        print("Dafuq")
        return

    guild = client.get_guild(payload.guild_id)  # You need the guild to get the member who reacted
    member = guild.get_member(payload.user_id)  # Now you have the key part, the member who should receive the role

    if payload.user_id == client.user.id:
        return

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
                if memberRole.id == int(os.environ['inviterRoleID']) or memberRole.id == int(
                        os.environ['recruiterRoleID']):
                    inviterBool = True
                    break
            if mentionMessage[0] == payload.message_id and str(payload.emoji) == str(
                    os.environ['emojiIDInviter']) and inviterBool:
                cur.execute("DELETE FROM mentionMessageTable WHERE id=%s;", (str(payload.message_id),))
                conn.commit()
                welcomeChannel = client.get_channel(int(os.environ['welcomeChannelID']))
                print("Message ID matches inviter ping message id, sending welcome message...")
                returningStr = ""
                if mentionMessage[2] == 1:
                    returningStr = "back "

                await welcomeChannel.send("Welcome " + returningStr + "<@" + mentionMessage[1] + ">" + "!" + """

You're now invited to the in-game clan, please check your inbox in-game!

To gain access to the clan dojo you'll have to build a Clan Key, you will be granted the blueprint for this immediately upon joining the clan in-game.

Feel free to ask us any questions you might have about the game.

Also please take a quick read through """ + client.get_channel(
                    389879532636733461).mention + """ and """ + client.get_channel(421809355676188701).mention + """

Have fun!""")
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
        role = guild.get_role(int(os.environ['roleIDMember']))  # You also need the role
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update):
            if entry.target.id == member.id:
                if entry.user.id == client.user.id:
                    return
        epicMember = []
        epicMember.insert(0, nickOrName(member))
        epicMember.insert(1, "Member")
        #DanisDGK Again, just insert epicMember[0] as the name and epicMember[1] as the role here.
        messageChannel = client.get_channel(int(os.environ['inviterChannelID']))

        if member.nick is not None and testing and "test" not in member.name.lower():
            if "*" in member.nick:
                await member.edit(nick=os.environ['emojiIDMember'] + " " + member.name.replace(" ", ""))
            else:
                await member.edit(nick=os.environ['emojiIDMember'] + " " + member.nick.replace(" ", ""))
            mentionMessageDab = await messageChannel.send(os.environ['inviterPingMessage'] + " and " + os.environ[

                'recruiterPingMessage'] + " please invite " + member.nick + " to the clan.")
            await mentionMessageDab.add_reaction(
                os.environ['emojiIDInviter'])
        elif member.nick is not None and testing and "test" in member.name.lower():
            if "*" in member.nick:
                await member.edit(nick=os.environ['emojiIDMember'] + " " + member.name.replace(" ", ""))
            else:
                await member.edit(nick=os.environ['emojiIDMember'] + " " + member.nick.replace(" ", ""))

        elif member.nick is not None and not testing and member.nick is not None:
            if "*" in member.nick:
                await member.edit(nick=os.environ['emojiIDMember'] + " " + member.name.replace(" ", ""))
            else:
                await member.edit(nick=os.environ['emojiIDMember'] + " " + member.nick.replace(" ", ""))
            mentionMessageDab = await messageChannel.send(os.environ['inviterPingMessage'] + " and " + os.environ[

                'recruiterPingMessage'] + " please invite " + member.nick + " to the clan.")
            await mentionMessageDab.add_reaction(
                os.environ['emojiIDInviter'])
        elif member.nick is None:
            errorMessage = await guild.get_channel(int(os.environ['guestChannelID'])).send(member.mention +
""" please read through this whole message before doing anything. 


If your Warframe ign and your discord username are different please change your discord nickname on this server to your warframe ign.

If your discord username is the same as your Warframe ign please change your discord nickname on this server to just "*"


To change your discord nickname on desktop you have to right click the mention (the first word in this message) and click on "Change Nickname". On mobile this is done by going to the channel selection menu by clicking on the three lines in the top left, pressing "Team Hydra" and then pressing "Change Nickname".

If you need help with any steps in this process feel free to contact any of the staff on the server (people with stars next to their names) and we’ll help you out.""")
            reactionChannel = client.get_channel(payload.channel_id)
            reactionMessage = await reactionChannel.get_message(payload.message_id)
            await reactionMessage.remove_reaction(payload.emoji, member)
            client.loop.create_task(deleteErrorMessage(errorMessage))
            return

        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cur = conn.cursor()
            cur.execute("INSERT INTO mentionMessageTable VALUES (%s, %s, False);",
                        (str(mentionMessageDab.id), str(payload.user_id)))
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
        await member.edit(nick=os.environ['emojiIDFriend'] + " " + nickOrName(member).replace(" ", ""))
        role = guild.get_role(int(os.environ['roleIDFriend']))
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update):
            if entry.target.id == member.id:
                if entry.user.id == client.user.id:
                    return
        epicMember = []
        epicMember.insert(0, nickOrName(member))
        epicMember.insert(1, "Friend")
        #DanisDGK Again, just insert epicMember[0] as the name and epicMember[1] as the role here.
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
        await member.add_roles(guild.get_role(int(os.environ['roleIDSeparator'])),
                               reason='Invited to clan')  # Finally add the role to the member
        await member.add_roles(guild.get_role(int(os.environ['tennoSeparator'])),
                               reason='Invited to clan')  # Finally add the role to the member
        await member.remove_roles(guild.get_role(int(os.environ['roleIDPending'])))
        print("Added role")

client.run(os.environ['discordToken'])
