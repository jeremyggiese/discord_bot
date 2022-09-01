
from code import interact
from typing import Literal, Union, NamedTuple
from enum import Enum
from dotenv import load_dotenv
import os
import discord
from discord import app_commands
from typing import Optional
load_dotenv()
TOKEN=os.getenv('DISCORD_TOKEN')
GUILD_ID=os.getenv('DISCORD_GUILD_ID')
MY_GUILD = discord.Object(GUILD_ID)  # replace with your guild id
EDIT_CHANNEL_ID=os.getenv('EDIT_CHANNEL_ID')
DELETED_CHANNEL_ID=os.getenv('DELETED_CHANNEL_ID')
ADVICE_CHANNEL_ID=os.getenv('ADVICE_CHANNEL_ID')
DEBATE_CHANNEL_ID=os.getenv('DEBATE_CHANNEL_ID')
ANNOUNCE_CHANNEL_ID=os.getenv('ANNOUNCE_CHANNEL_ID')
INTRODUCE_CHANNEL_ID=os.getenv('INTRODUCE_CHANNEL_ID')
REPORT_CHANNEL_ID=os.getenv('REPORT_CHANNEL_ID')
QUOTES_CHANNEL_ID=os.getenv('QUOTES_CHANNEL_ID')

class MyClient(discord.Client):
    def __init__(self):
        intents=discord.Intents.default()
        intents.message_content=True
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

client=MyClient()


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
@client.event
async def on_member_join(member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f'Welcome {member.mention} to {guild.name}! Try using the /introduce command to write an introduction.'
        await guild.system_channel.send(to_send)
if(EDIT_CHANNEL_ID):
    @client.event
    async def on_message_edit(before, after):
            msg = f'**{before.author}** edited their message:\n{before.content} -> {after.content}\n in {before.channel.mention}'
            edit_channel=discord.utils.get(client.get_all_channels(), channel_id=int(EDIT_CHANNEL_ID))
            await edit_channel.send(msg)
if(DELETED_CHANNEL_ID):
    @client.event
    async def on_message_delete(message):
            if(message.author!=client.user):
                msg = f'**{message.author}** deleted their message:\n"{message.content}" in {message.channel.mention}'
                delete_channel=discord.utils.get(client.get_all_channels(), channel_id=int(DELETED_CHANNEL_ID))
                await delete_channel.send(msg)


# Other transformers include regular type hints that are supported by Discord
# Examples of these include int, str, float, bool, User, Member, Role, and any channel type.
# Since there are a lot of these, for brevity only a channel example will be included.

# This command shows how to only show text and voice channels to a user using the Union type hint
# combined with the VoiceChannel and TextChannel types.

@client.tree.command(name='channel-info')
@app_commands.describe(channel='The channel to get info of')
async def channel_info(interaction: discord.Interaction, channel: Union[discord.VoiceChannel, discord.TextChannel]):
    """Shows basic channel info for a text or voice channel."""

    embed = discord.Embed(title='Channel Info')
    embed.add_field(name='Name', value=channel.name, inline=True)
    embed.add_field(name='ID', value=channel.id, inline=True)
    embed.add_field(
        name='Type',
        value='Voice' if isinstance(channel, discord.VoiceChannel) else 'Text',
        inline=True,
    )

    embed.set_footer(text='Created').timestamp = channel.created_at
    await interaction.response.send_message(embed=embed)


# In order to support choices, the library has a few ways of doing this.
# The first one is using a typing.Literal for basic choices.

# On Discord, this will show up as two choices, Buy and Sell.
# In the code, you will receive either 'Buy' or 'Sell' as a string.
""" @client.tree.command()
@app_commands.describe(action='The action to do in the shop', item='The target item')
async def shop(interaction: discord.Interaction, action: Literal['Buy', 'Sell'], item: str):
    "Interact with the shop"
    await interaction.response.send_message(f'Action: {action}\nItem: {item}') """
if(ADVICE_CHANNEL_ID is not None):
    class request_types(Enum):
        do_not_interact=0
        request_advice=1
        dm_advice=2
    class anon(Enum):
        with_name=0
        anonymous=1

    @client.tree.command()
    @app_commands.describe(type='What type of advice is needed?')
    async def request_advice(interaction: discord.Interaction, type:request_types, anon:anon, value:str):
        if(type.value==0):
            value="||"+value+"||"
        if(anon.value==1 and type.value>0):
            await interaction.response.send_message(f'Illegal options', ephemeral=True)
        else:
            if(anon.value==0):
                member=interaction.user
            advice_channel=interaction.guild.get_channel(int(ADVICE_CHANNEL_ID))

            await interaction.response.send_message(f'Advice requested in {advice_channel.mention}', ephemeral=True)
            await advice_channel.send(f'{type.name.replace("_", " ").capitalize()} \n\n{member} says:\n\"{value}\"')

# To make an argument optional, you can either give it a supported default argument
# or you can mark it as Optional from the typing standard library. This example does both.
if(DEBATE_CHANNEL_ID is not None):
    @client.tree.command()
    @app_commands.describe(member='The member you want to debate', topic='What is the topic of the debate?')
    async def debate(interaction: discord.Interaction, topic:str, member: Optional[discord.Member] = None):
        
        # If no member is explicitly provided then we use the command user here
        if(member):
            response=f'{interaction.user.display_name} would like to debate with {member.mention} surrounding the following\n\n{topic}'
        else:
        # The format_dt function formats the date time into a human readable representation in the official client
            response=(f'{interaction.user.display_name} would like to debate the following\n{topic}')
        debate_channel = interaction.guild.get_channel(int(DEBATE_CHANNEL_ID))  # replace with your channel id
        await interaction.response.send_message(f'Debate communicated in {debate_channel.mention}', ephemeral=True)
        await debate_channel.send(response)
    


# To make an argument optional, you can either give it a supported default argument
# or you can mark it as Optional from the typing standard library. This example does both.
@client.tree.command()
@app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Says when a member joined."""
    # If no member is explicitly provided then we use the command user here
    member = member or interaction.user

    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')
if(ANNOUNCE_CHANNEL_ID is not None):
    # This context menu command only works on messages
    @client.tree.command()
    async def announce(interaction: discord.Interaction, value:str):
        # We're sending this response message with ephemeral=True, so only the command executor can see it
        await interaction.response.send_message(
            f'Announcing {value}', ephemeral=True
        )
        member=interaction.user
        # Handle report by sending it into a log channel
        announce_channel = interaction.guild.get_channel(int(ANNOUNCE_CHANNEL_ID))  # replace with your channel id
        
        value=f'Announcement from {member.mention}\n'+value
    

        await announce_channel.send(value)

if(INTRODUCE_CHANNEL_ID is not None):
    @client.tree.command()
    async def introduce(interaction: discord.Interaction, value:str):
        # We're sending this response message with ephemeral=True, so only the command executor can see it
        await interaction.response.send_message(
            f'Introduction is:\n {value}', ephemeral=True
        )
        #member=interaction.user
        introduction_channel = interaction.guild.get_channel(int(INTRODUCE_CHANNEL_ID))  # replace with your channel id
        embed = discord.Embed()
        embed.description = value
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        #embed.timestamp = 
        #footer=f'Quoted by {interaction.user}'
        #embed.set_footer(text=footer)
        url_view = discord.ui.View()
        #url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

        await introduction_channel.send(embed=embed, view=url_view)
        # Handle report by sending it into a log channel
  


# A Context Menu command is an app command that can be run on a member or on a message by
# accessing a menu within the client, usually via right clicking.
# It always takes an interaction as its first parameter and a Member or Message as its second parameter.

# This context menu command only works on members
@client.tree.context_menu(name='Show Join Date')
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')

if(REPORT_CHANNEL_ID is not None):
    # This context menu command only works on messages
    @client.tree.context_menu(name='Report to Moderators')
    async def report_message(interaction: discord.Interaction, message: discord.Message):
        # We're sending this response message with ephemeral=True, so only the command executor can see it
        await interaction.response.send_message(
            f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
        )

        # Handle report by sending it into a log channel
        log_channel = interaction.guild.get_channel(int(REPORT_CHANNEL_ID))  # replace with your channel id

        embed = discord.Embed(title='Reported Message')
        if message.content:
            embed.description = message.content

        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.timestamp = message.created_at

        url_view = discord.ui.View()
        url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

        await log_channel.send(embed=embed, view=url_view)
if(QUOTES_CHANNEL_ID is not None):
    # This context menu command only works on messages
    @client.tree.context_menu(name='Quote')
    async def report_message(interaction: discord.Interaction, message: discord.Message):
        # We're sending this response message with ephemeral=True, so only the command executor can see it
        await interaction.response.send_message(
            f'This message by {message.author.mention} has been added to quotes', ephemeral=True
        )

        # Handle report by sending it into a log channel
        quotes_channel = interaction.guild.get_channel(int(QUOTES_CHANNEL_ID))  # replace with your channel id
        embed = discord.Embed()
        if message.content:
            embed.description = f'>>> {message.content}'

        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.timestamp = message.created_at
        footer=f'Quoted by {interaction.user}'
        embed.set_footer(text=footer)
        url_view = discord.ui.View()
        url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

        await quotes_channel.send(embed=embed, view=url_view)


client.run(TOKEN)