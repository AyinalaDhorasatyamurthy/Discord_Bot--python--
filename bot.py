"""
Discord Bot - Main Entry Point
A comprehensive Discord bot with commands, moderation, music, AI, and more.
"""

import os
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
BOT_PREFIX = os.getenv('BOT_PREFIX', '!')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# Create bot instance
bot = commands.Bot(
    command_prefix=BOT_PREFIX,
    intents=intents,
    help_command=commands.DefaultHelpCommand(),
    case_insensitive=True
)

# Create necessary directories
Path('data').mkdir(exist_ok=True)


@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    logger.info(f'Bot is ready! Logged in as {bot.user.name}#{bot.user.discriminator}')
    logger.info(f'Bot ID: {bot.user.id}')
    logger.info(f'Connected to {len(bot.guilds)} guild(s)')
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{BOT_PREFIX}help for commands"
        )
    )
    
    # Load cogs
    await load_cogs()
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logger.info(f'Synced {len(synced)} slash command(s)')
    except Exception as e:
        logger.error(f'Failed to sync slash commands: {e}')


async def load_cogs():
    """Load all command cogs."""
    cogs_dir = Path('cogs')
    if cogs_dir.exists():
        for file in cogs_dir.glob('*.py'):
            if file.name != '__init__.py':
                try:
                    await bot.load_extension(f'cogs.{file.stem}')
                    logger.info(f'Loaded cog: {file.stem}')
                except Exception as e:
                    logger.error(f'Failed to load cog {file.stem}: {e}')


@bot.event
async def on_guild_join(guild):
    """Called when the bot joins a new guild."""
    logger.info(f'Joined new guild: {guild.name} (ID: {guild.id})')
    
    # Try to send welcome message to system channel
    if guild.system_channel:
        embed = discord.Embed(
            title="Thanks for inviting me! 🎉",
            description=f"Hi! I'm {bot.user.name}, a feature-rich Discord bot.\n\n"
                       f"Use `{BOT_PREFIX}help` to see all available commands!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Quick Start",
            value=f"Try `{BOT_PREFIX}hello` to greet me!",
            inline=False
        )
        try:
            await guild.system_channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning(f'Cannot send message to {guild.name} system channel')


@bot.event
async def on_member_join(member):
    """Called when a new member joins the server."""
    logger.info(f'{member.name} joined {member.guild.name}')
    
    # Welcome message
    if member.guild.system_channel:
        embed = discord.Embed(
            title=f"Welcome to {member.guild.name}! 🎉",
            description=f"Hey {member.mention}, welcome to the server!\n\n"
                       f"We're glad to have you here. Make sure to read the rules!",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        try:
            await member.guild.system_channel.send(embed=embed)
        except discord.Forbidden:
            pass


@bot.event
async def on_message(message):
    """Process all messages."""
    # Don't process messages from bots
    if message.author.bot:
        return
    
    # Debug logging to verify messages are received
    logger.info(f"Received message from {message.author} in {message.channel.name}: {message.content}")
    
    # Process commands FIRST - this should only happen once!
    await bot.process_commands(message)
    
    # If the message was a command, stop here to avoid double-processing
    ctx = await bot.get_context(message)
    if ctx.valid:
        return
    
    # Get the AI cog instance
    ai_cog = bot.get_cog('AI')
    if not ai_cog:
        logger.warning("AI cog not loaded")
        return

    content = message.content.strip()
    if not content or content.startswith(bot.command_prefix):
        return

    # Check if message needs an AI response (questions, emotional expressions, or statements)
    needs_response = any([
        # Questions
        any(word in content.lower().split() for word in ['who', 'what', 'when', 'where', 'why', 'how']),
        '?' in content,
        any(phrase in content.lower() for phrase in ['tell me about', 'explain', 'what is', 'who is']),
        
        # Emotional expressions
        any(word in content.lower() for word in ['angry', 'happy', 'sad', 'excited', 'bored', 'tired']),
        content.lower().startswith(('i am ', 'i\'m ', 'i feel ')),
        
        # General statements that might need a response
        len(content.split()) > 3 and not content.endswith(('.', '!', '?')),  # Longer statements without punctuation
        any(word in content.lower() for word in ['fabulous', 'amazing', 'great', 'awesome'])
    ])

    if needs_response:
        async with message.channel.typing():
            response = await ai_cog.get_ai_response(content)
            if not response.startswith("❌"):
                embed = discord.Embed(
                    description=response,
                    color=discord.Color.blue()
                )
                await message.reply(embed=embed, mention_author=False)
    
    # Smart positive word detection with contextual responses
    # Dictionary mapping words to their contextual responses
    word_responses = {
        # Excitement words
        'wow': [f'Wow {message.author.mention}! 😲', f'Amazing {message.author.mention}! ✨', f'That\'s awesome {message.author.mention}! 🎉'],
        'woah': [f'Woah {message.author.mention}! 😲', f'Wow {message.author.mention}! ✨'],
        'whoa': [f'Whoa {message.author.mention}! 😲', f'Amazing {message.author.mention}! ✨'],
        'amazing': [f'Amazing {message.author.mention}! ✨', f'You\'re amazing too {message.author.mention}! 🌟'],
        'awesome': [f'Awesome {message.author.mention}! 🔥', f'You\'re awesome too {message.author.mention}! 😎'],
        'fantastic': [f'Fantastic {message.author.mention}! 🌈', f'That\'s fantastic {message.author.mention}! 🎊'],
        'incredible': [f'Incredible {message.author.mention}! 🔥', f'That\'s incredible {message.author.mention}! 🌟'],
        'brilliant': [f'Brilliant {message.author.mention}! 💡', f'That\'s brilliant {message.author.mention}! 🌟'],
        'wonderful': [f'Wonderful {message.author.mention}! 🌈', f'That\'s wonderful {message.author.mention}! ✨'],
        'super': [f'Super {message.author.mention}! 🚀', f'That\'s super {message.author.mention}! ✨'],
        'sweet': [f'Sweet {message.author.mention}! 🍬', f'That\'s sweet {message.author.mention}! 😊'],
        'epic': [f'Epic {message.author.mention}! 🎮', f'That\'s epic {message.author.mention}! 🔥'],
        'legendary': [f'Legendary {message.author.mention}! 💎', f'That\'s legendary {message.author.mention}! 🌟'],
        'marvelous': [f'Marvelous {message.author.mention}! ✨', f'That\'s marvelous {message.author.mention}! 🌟'],
        'magnificent': [f'Magnificent {message.author.mention}! 👑', f'That\'s magnificent {message.author.mention}! 🌟'],
        
        # Praise words
        'great': [f'Great {message.author.mention}! 👍', f'That\'s great {message.author.mention}! 🎊'],
        'good': [f'That\'s good {message.author.mention}! 👍', f'Good {message.author.mention}! 😊'],
        'nice': [f'Nice {message.author.mention}! 😊', f'That\'s nice {message.author.mention}! ✨'],
        'cool': [f'Cool {message.author.mention}! 😎', f'That\'s cool {message.author.mention}! ✨'],
        'excellent': [f'Excellent {message.author.mention}! 🎯', f'Great job {message.author.mention}! 🌟'],
        'perfect': [f'Perfect {message.author.mention}! ✅', f'That\'s perfect {message.author.mention}! ✨'],
        'outstanding': [f'Outstanding {message.author.mention}! 🏆', f'That\'s outstanding {message.author.mention}! 🌟'],
        'remarkable': [f'Remarkable {message.author.mention}! ✨', f'That\'s remarkable {message.author.mention}! 🌟'],
        'splendid': [f'Splendid {message.author.mention}! 🌟', f'That\'s splendid {message.author.mention}! ✨'],
        'terrific': [f'Terrific {message.author.mention}! 🎉', f'That\'s terrific {message.author.mention}! 🌟'],
        'fabulous': [f'Fabulous {message.author.mention}! ✨', f'That\'s fabulous {message.author.mention}! 🌈'],
        'phenomenal': [f'Phenomenal {message.author.mention}! 🔥', f'That\'s phenomenal {message.author.mention}! 🌟'],
        'spectacular': [f'Spectacular {message.author.mention}! 🎆', f'That\'s spectacular {message.author.mention}! ✨'],
        
        # Achievement words
        'congrats': [f'Congratulations {message.author.mention}! 🎉🎊', f'Well done {message.author.mention}! 👏', f'Congrats {message.author.mention}! 🏆'],
        'congratulations': [f'Congratulations {message.author.mention}! 🎉🎊', f'Amazing achievement {message.author.mention}! 🏆'],
        'bravo': [f'Bravo {message.author.mention}! 👏', f'Well done {message.author.mention}! 🎉'],
        'kudos': [f'Kudos {message.author.mention}! 👏', f'Great job {message.author.mention}! 🌟'],
        
        # Appreciation words
        'thanks': [f'You\'re welcome {message.author.mention}! 😊', f'Happy to help {message.author.mention}! 🙌', f'Any time {message.author.mention}! 💙'],
        'thank': [f'You\'re welcome {message.author.mention}! 😊', f'Happy to help {message.author.mention}! 🙌'],
        'appreciate': [f'You\'re welcome {message.author.mention}! 😊', f'Happy to help {message.author.mention}! 🙌'],
        
        # Agreement words
        'yeah': [f'Yeah {message.author.mention}! 👍', f'Right on {message.author.mention}! ✨'],
        'yes': [f'Great {message.author.mention}! 👍', f'Awesome {message.author.mention}! 😊'],
        'yay': [f'Yay {message.author.mention}! 🎉', f'That\'s great {message.author.mention}! 🌟'],
        'yep': [f'Yep {message.author.mention}! 👍', f'Right on {message.author.mention}! ✨'],
        'yup': [f'Yup {message.author.mention}! 👍', f'Exactly {message.author.mention}! 🎯'],
        'okay': [f'Okay {message.author.mention}! 👍', f'Sounds good {message.author.mention}! 😊'],
        'ok': [f'Okay {message.author.mention}! 👍', f'Sounds good {message.author.mention}! 😊'],
        
        # Fun words
        'fun': [f'Glad you\'re having fun {message.author.mention}! 🎮', f'Fun is the best {message.author.mention}! 🎈'],
        'enjoy': [f'Glad you\'re enjoying {message.author.mention}! 🎉', f'Enjoy {message.author.mention}! 🎈'],
        'enjoying': [f'Glad you\'re enjoying {message.author.mention}! 🎉', f'That\'s great {message.author.mention}! 🎈'],
        'loved': [f'Glad you loved it {message.author.mention}! ❤️', f'That\'s wonderful {message.author.mention}! 💙'],
        'love': [f'Love it too {message.author.mention}! ❤️', f'That\'s awesome {message.author.mention}! 💙'],
        'loving': [f'Glad you\'re loving it {message.author.mention}! ❤️', f'That\'s great {message.author.mention}! 💙'],
        
        # Surprise words (including common misspellings)
        'surprise': [f'Surprise! {message.author.mention}! 🎁', f'Wow {message.author.mention}! That\'s surprising! 😲'],
        'surprised': [f'Surprised {message.author.mention}? 😲', f'That\'s surprising {message.author.mention}! ✨'],
        'surprising': [f'That\'s surprising {message.author.mention}! 😲', f'Amazing {message.author.mention}! ✨'],
        'shocked': [f'Shocked {message.author.mention}? 😲', f'That\'s shocking {message.author.mention}! ⚡'],
        'shocking': [f'That\'s shocking {message.author.mention}! ⚡', f'Wow {message.author.mention}! 😲'],
        'shoked': [f'Shocked {message.author.mention}? 😲', f'That\'s shocking {message.author.mention}! ⚡'],  # Common misspelling
        'shokd': [f'Shocked {message.author.mention}? 😲', f'That\'s shocking {message.author.mention}! ⚡'],  # Common misspelling
        
        # Emotion words
        'happy': [f'Glad you\'re happy {message.author.mention}! 😊', f'Happiness is great {message.author.mention}! 🌈'],
        'happiness': [f'Happiness is wonderful {message.author.mention}! 😊', f'That\'s great {message.author.mention}! 🌈'],
        'joy': [f'Joy is amazing {message.author.mention}! 😊', f'Glad you feel joy {message.author.mention}! 🌈'],
        'joyful': [f'Joyful {message.author.mention}! 😊', f'That\'s wonderful {message.author.mention}! 🌈'],
        'excited': [f'Excited {message.author.mention}? 🎉', f'That\'s exciting {message.author.mention}! ✨'],
        'exciting': [f'That\'s exciting {message.author.mention}! 🎉', f'Great {message.author.mention}! ✨'],
        'thrilled': [f'Thrilled {message.author.mention}? 🎉', f'That\'s thrilling {message.author.mention}! ✨'],
        'thrilling': [f'That\'s thrilling {message.author.mention}! 🎉', f'Great {message.author.mention}! ✨'],
        'proud': [f'Proud of you {message.author.mention}! 👏', f'That\'s something to be proud of {message.author.mention}! 🌟'],
        'pleased': [f'Pleased {message.author.mention}? 😊', f'That\'s great {message.author.mention}! ✨'],
        'delighted': [f'Delighted {message.author.mention}? 😊', f'That\'s wonderful {message.author.mention}! 🌟'],
        'glad': [f'Glad to hear {message.author.mention}! 😊', f'That\'s great {message.author.mention}! ✨'],
        'ecstatic': [f'Ecstatic {message.author.mention}? 🎉', f'That\'s amazing {message.author.mention}! ✨'],
        'overjoyed': [f'Overjoyed {message.author.mention}? 🎉', f'That\'s wonderful {message.author.mention}! 🌟'],
        
        # Lucky words
        'lucky': [f'Lucky {message.author.mention}! 🍀', f'That\'s lucky {message.author.mention}! ✨'],
        'luck': [f'Good luck {message.author.mention}! 🍀', f'That\'s lucky {message.author.mention}! ✨'],
        'fortune': [f'Fortune {message.author.mention}! 🍀', f'That\'s fortunate {message.author.mention}! ✨'],
    }
    
    # Negative words that should NOT trigger responses
    negative_words = {'sad', 'angry', 'bad', 'terrible', 'awful', 'horrible', 'disappointed', 
                     'upset', 'mad', 'hate', 'hated', 'depressed', 'lonely', 'tired', 'exhausted',
                     'bored', 'annoyed', 'frustrated', 'worried', 'scared', 'afraid', 'fear'}
    
    # Check if message contains negative words first - don't respond if it does
    words_in_message = set(content_lower.split())
    if negative_words.intersection(words_in_message):
        # Contains negative words - don't respond positively
        return
    
    # Find the best matching word (prioritize longer/more specific words)
    matched_word = None
    matched_responses = None
    
    # Check for exact matches first (prioritize longer words for better specificity)
    for word in sorted(word_responses.keys(), key=len, reverse=True):
        if word in words_in_message:
            matched_word = word
            matched_responses = word_responses[word]
            break
    
    if matched_word and matched_responses:
        import random
        try:
            await message.channel.send(random.choice(matched_responses))
        except (discord.Forbidden, discord.HTTPException):
            pass
        return


@bot.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    if isinstance(error, commands.CommandNotFound):
        # Silently ignore unknown commands
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument. Use `{BOT_PREFIX}help {ctx.command.name}` for usage.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏰ This command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I don't have the required permissions to execute this command.")
    else:
        logger.error(f'Command error: {error}', exc_info=error)
        await ctx.send(f"❌ An error occurred: {str(error)}")


@bot.command(name='reload', aliases=['rl'])
@commands.is_owner()
async def reload_cogs(ctx):
    """Reload all cogs (owner only)."""
    cogs_dir = Path('cogs')
    reloaded = []
    failed = []
    
    for file in cogs_dir.glob('*.py'):
        if file.name != '__init__.py':
            try:
                await bot.reload_extension(f'cogs.{file.stem}')
                reloaded.append(file.stem)
            except Exception as e:
                failed.append(f"{file.stem}: {str(e)}")
    
    embed = discord.Embed(title="Cog Reload Status", color=discord.Color.blue())
    if reloaded:
        embed.add_field(name="✅ Reloaded", value="\n".join(reloaded), inline=False)
    if failed:
        embed.add_field(name="❌ Failed", value="\n".join(failed), inline=False)
    
    await ctx.send(embed=embed)


@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency."""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latency: {latency}ms",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


@bot.command(name='invite')
async def invite(ctx):
    """Get bot invite link."""
    invite_url = discord.utils.oauth_url(
        bot.user.id,
        permissions=discord.Permissions(
            send_messages=True,
            manage_messages=True,
            embed_links=True,
            attach_files=True,
            connect=True,
            speak=True,
            kick_members=True,
            ban_members=True,
            moderate_members=True,
            read_message_history=True
        ),
        scopes=['bot', 'applications.commands']
    )
    
    embed = discord.Embed(
        title="🔗 Invite Link",
        description=f"[Click here to invite me to your server!]({invite_url})",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)


def main():
    """Main function to run the bot."""
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        logger.error("Please create a .env file with your bot token.")
        return
    
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error("Invalid token! Please check your DISCORD_TOKEN in .env")
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)


if __name__ == '__main__':
    main()