import discord
import yaml
import os
import sys

intents = discord.Intents.all()
client = discord.Client(intents=intents)

f = open("key.txt", "r")
api_key = f.read()

config_path = os.path.join(sys.path[0], 'config.yml')
stream = open(config_path, 'r')
data = yaml.safe_load(stream)
print("config file loaded")

watched_message = data['message_id']
role_dict = data['roles']
mandatory_role_dict = data['mandatory_roles']
welcome_message = data['welcome_message']
followup_message = data['followup_message']
snge_ranks = ["Enforcer", "Aspirant Warden", "Warden", "Sanguinary Guard"]


async def manage_reaction(payload):

    if payload.guild_id is None:
        return  # Reaction is on a private message

    if payload.user_id == 745310932997242950:
        return # id of this bot

    if payload.message_id != watched_message:
        return # Reaction is not on the selection message

    guild = await client.fetch_guild(payload.guild_id)
    member = await guild.fetch_member(payload.user_id)

    #print(payload.channel_id)
    #print(guild.name)
    print(member.name + ' ' + str(member.id))
    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    emoji = payload.emoji.name

    if (not emoji in role_dict) and (not emoji in mandatory_role_dict):
        print("unknown emoji")
        await message.clear_reaction(payload.emoji)
        return

    if payload.event_type == "REACTION_ADD":

        if emoji in mandatory_role_dict:
            role = discord.utils.get(guild.roles, name=mandatory_role_dict[emoji])
        else:
            role = discord.utils.get(guild.roles, name=role_dict[emoji])

        await member.add_roles(role)
        print("role added")

    else: # event reaction remove
        if emoji in role_dict:
            role = discord.utils.get(guild.roles, name=role_dict[emoji])
            await member.remove_roles(role)
            print("role removed")

        else: # emoji is mandatory for SNGE members
            mroles = (r.name for r in member.roles)
            if set(mroles).isdisjoint(snge_ranks): # the member is not part of SNGE
                role = discord.utils.get(guild.roles, name=mandatory_role_dict[emoji])
                await member.remove_roles(role)
                print("mandatory role removed")
            else:
                print("cannot remove mandatory role")


@client.event
async def on_raw_reaction_add(payload):
    await manage_reaction(payload)


@client.event
async def on_raw_reaction_remove(payload):
    await manage_reaction(payload)


@client.event
async def on_member_join(member):
    print("new member joined!")
    for channel in member.guild.channels:
        if channel.name == 'sanctuary':
            await channel.send(member.mention + ' ' + welcome_message)
            await channel.send(followup_message)

client.run(api_key)
