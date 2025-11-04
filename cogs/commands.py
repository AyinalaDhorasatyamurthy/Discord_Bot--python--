"""
Basic Commands Cog
Handles basic commands like help, hello, meme, serverinfo, etc.
"""

import discord
from discord.ext import commands
import aiohttp
import json
import os
import asyncio
from pathlib import Path


class BasicCommands(commands.Cog):
    """Basic bot commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
    
    @commands.command(name='hello', aliases=['hi', 'hey'])
    async def hello(self, ctx):
        """Greet the bot."""
        greetings = [
            f"Hello {ctx.author.mention}! 👋",
            f"Hey there {ctx.author.mention}! 😊",
            f"Hi {ctx.author.mention}! How can I help you?",
            f"Greetings {ctx.author.mention}! 🎉"
        ]
        import random
        await ctx.send(random.choice(greetings))
    
    @commands.command(name='meme', aliases=['memes'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme_command(self, ctx, subreddit: str = None):
        """Fetch a random meme from Reddit. Usage: !meme [subreddit]"""
        if subreddit is None:
            subreddit = 'memes'
        
        # Use typing() instead of trigger_typing() for discord.py 2.x
        async with ctx.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    # Import random for selecting random posts
                    import random
                    import time
                    
                    # Use cache-busting parameter to ensure we get different results
                    cache_buster = int(time.time() * 1000)
                    
                    # Try multiple Reddit endpoints with different sorting and cache-busting
                    # Fetch multiple posts to ensure variety
                    urls_to_try = [
                        f"https://www.reddit.com/r/{subreddit}/hot.json?limit=25&t=day&raw_json=1&{cache_buster}",
                        f"https://www.reddit.com/r/{subreddit}/new.json?limit=25&raw_json=1&{cache_buster}",
                        f"https://www.reddit.com/r/{subreddit}/top.json?limit=25&t=day&raw_json=1&{cache_buster}",
                        f"https://www.reddit.com/r/{subreddit}/random.json?raw_json=1&{cache_buster}",
                    ]
                    
                    # Realistic browser headers to avoid blocking
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'application/json, text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    }
                    
                    response = None
                    data = None
                    
                    # Try each URL until one works
                    all_posts = []
                    for url in urls_to_try:
                        try:
                            async with session.get(url, headers=headers, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                                if resp.status == 200:
                                    try:
                                        data = await resp.json()
                                        
                                        # Extract posts from response
                                        posts = []
                                        if isinstance(data, list) and len(data) > 0:
                                            children = data[0].get('data', {}).get('children', [])
                                            posts = [child.get('data', {}) for child in children if child.get('data', {}).get('title')]
                                        elif isinstance(data, dict):
                                            children = data.get('data', {}).get('children', [])
                                            posts = [child.get('data', {}) for child in children if child.get('data', {}).get('title')]
                                        
                                        # Filter out stickied posts and non-image posts if possible
                                        valid_posts = []
                                        for p in posts:
                                            # Skip stickied posts
                                            if not p.get('stickied', False):
                                                valid_posts.append(p)
                                        
                                        if valid_posts:
                                            all_posts.extend(valid_posts)
                                            # If we got enough posts, break
                                            if len(all_posts) >= 10:
                                                break
                                    except (aiohttp.ContentTypeError, KeyError, IndexError, TypeError):
                                        continue  # Try next URL
                                elif resp.status == 403:
                                    continue  # Try next URL
                                else:
                                    continue  # Try next URL
                        except (aiohttp.ClientError, asyncio.TimeoutError):
                            continue  # Try next URL
                    
                    if not all_posts:
                        await ctx.send(f"❌ Unable to fetch memes from r/{subreddit}. Reddit may be blocking automated requests.\n\n💡 **Tip:** Try again in a few minutes, or the subreddit might be private/restricted.")
                        return
                    
                    # Randomly select a post from the collected posts
                    post = random.choice(all_posts)
                    
                    if not post or not post.get('title'):
                        await ctx.send("❌ No meme found. Try again!")
                        return
                    
                    embed = discord.Embed(
                        title=post.get('title', 'Meme')[:256],  # Discord limit
                        url=f"https://reddit.com{post.get('permalink', '')}",
                        color=discord.Color.orange()
                    )
                    
                    # Handle image or video
                    post_url = post.get('url', '')
                    if post_url:
                        # Check if it's an image
                        if any(post_url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.gifv', '.webp']):
                            embed.set_image(url=post_url)
                        elif 'i.redd.it' in post_url or 'imgur.com' in post_url or 'i.imgur.com' in post_url:
                            embed.set_image(url=post_url)
                        elif post.get('preview') and post['preview'].get('images'):
                            # Try to get preview image
                            try:
                                images = post['preview']['images'][0]['source']['url']
                                embed.set_image(url=images.replace('&amp;', '&'))
                            except (KeyError, IndexError):
                                embed.description = f"[View Content]({post_url})"
                        else:
                            embed.description = f"[View Content]({post_url})"
                    
                    upvotes = post.get('ups', 0) or 0
                    comments = post.get('num_comments', 0) or 0
                    embed.set_footer(text=f"👍 {upvotes:,} | 💬 {comments:,} | r/{subreddit}")
                    
                    await ctx.send(embed=embed)
            except aiohttp.ClientError as e:
                await ctx.send(f"❌ Network error: Could not connect to Reddit. Please try again later.")
            except asyncio.TimeoutError:
                await ctx.send(f"❌ Request timed out. Reddit may be slow. Try again!")
            except Exception as e:
                await ctx.send(f"❌ Error fetching meme: {str(e)[:200]}")
                # Log full error for debugging
                import logging
                logging.error(f"Meme command error: {e}", exc_info=True)
    
    @discord.app_commands.command(name='meme', description='Fetch a random meme from Reddit')
    @discord.app_commands.describe(subreddit='The subreddit to fetch memes from (default: memes)')
    async def meme_slash(self, interaction: discord.Interaction, subreddit: str = 'memes'):
        """Slash command version of meme."""
        
        await interaction.response.defer()
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://www.reddit.com/r/{subreddit}/random.json"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with session.get(url, headers=headers, allow_redirects=True) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        post = None
                        if isinstance(data, list) and len(data) > 0:
                            post_data = data[0].get('data', {}).get('children', [])
                            if post_data and len(post_data) > 0:
                                post = post_data[0].get('data', {})
                        elif isinstance(data, dict):
                            children = data.get('data', {}).get('children', [])
                            if children and len(children) > 0:
                                post = children[0].get('data', {})
                        
                        if not post:
                            await interaction.followup.send("❌ No meme found. Try again!")
                            return
                        
                        embed = discord.Embed(
                            title=post.get('title', 'Meme')[:256],
                            url=f"https://reddit.com{post.get('permalink', '')}",
                            color=discord.Color.orange()
                        )
                        
                        post_url = post.get('url', '')
                        if post_url:
                            if any(post_url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.gifv', '.webp']):
                                embed.set_image(url=post_url)
                            elif 'i.redd.it' in post_url or 'imgur.com' in post_url:
                                embed.set_image(url=post_url)
                            elif post.get('preview'):
                                try:
                                    images = post['preview']['images'][0]['source']['url']
                                    embed.set_image(url=images.replace('&amp;', '&'))
                                except:
                                    embed.description = f"[View Content]({post_url})"
                            else:
                                embed.description = f"[View Content]({post_url})"
                        
                        upvotes = post.get('ups', 0)
                        comments = post.get('num_comments', 0)
                        embed.set_footer(text=f"👍 {upvotes:,} | 💬 {comments:,} | r/{subreddit}")
                        
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send(f"❌ Could not fetch meme from r/{subreddit}")
        except Exception as e:
            await interaction.followup.send(f"❌ Error fetching meme: {str(e)[:200]}")
    
    @commands.command(name='serverinfo', aliases=['server', 'guildinfo'])
    async def serverinfo(self, ctx):
        """Display server information."""
        guild = ctx.guild
        
        # Count members by status
        online = sum(1 for m in guild.members if m.status == discord.Status.online)
        idle = sum(1 for m in guild.members if m.status == discord.Status.idle)
        dnd = sum(1 for m in guild.members if m.status == discord.Status.dnd)
        offline = sum(1 for m in guild.members if m.status == discord.Status.offline)
        
        embed = discord.Embed(
            title=f"{guild.name} Server Information",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="🆔 Server ID", value=guild.id, inline=True)
        embed.add_field(name="📅 Created", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        
        embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
        embed.add_field(name="🤖 Bots", value=sum(1 for m in guild.members if m.bot), inline=True)
        embed.add_field(name="📝 Roles", value=len(guild.roles), inline=True)
        
        embed.add_field(
            name="💚 Status",
            value=f"🟢 {online} | 🟡 {idle} | 🔴 {dnd} | ⚪ {offline}",
            inline=False
        )
        
        embed.add_field(name="📁 Channels", value=f"💬 {len(guild.text_channels)} | 🔊 {len(guild.voice_channels)}", inline=True)
        embed.add_field(name="✅ Verification", value=str(guild.verification_level).title(), inline=True)
        embed.add_field(name="😀 Emojis", value=len(guild.emojis), inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='userinfo', aliases=['user', 'whois'])
    async def userinfo(self, ctx, member: discord.Member = None):
        """Display user information."""
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f"{member.display_name}'s Information",
            color=member.color if member.color != discord.Color.default() else discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        embed.add_field(name="👤 Username", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="🆔 User ID", value=member.id, inline=True)
        embed.add_field(name="📅 Account Created", value=member.created_at.strftime("%B %d, %Y"), inline=False)
        embed.add_field(name="📥 Joined Server", value=member.joined_at.strftime("%B %d, %Y") if member.joined_at else "Unknown", inline=True)
        
        # Roles
        roles = [role.mention for role in member.roles[1:]]  # Exclude @everyone
        roles_str = ", ".join(roles) if roles else "None"
        if len(roles_str) > 1024:
            roles_str = roles_str[:1021] + "..."
        embed.add_field(name="🎭 Roles", value=roles_str or "None", inline=False)
        
        embed.add_field(name="📊 Status", value=str(member.status).title(), inline=True)
        embed.add_field(name="🤖 Bot", value="Yes" if member.bot else "No", inline=True)
        
        if member.activity:
            activity_type = str(member.activity.type).split('.')[-1].title()
            embed.add_field(name="🎮 Activity", value=f"{activity_type}: {member.activity.name}", inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='avatar', aliases=['av', 'pfp'])
    async def avatar(self, ctx, member: discord.Member = None):
        """Display a user's avatar."""
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f"{member.display_name}'s Avatar",
            color=member.color if member.color != discord.Color.default() else discord.Color.blue()
        )
        
        if member.avatar:
            embed.set_image(url=member.avatar.url)
        else:
            embed.description = "User has no avatar."
        
        embed.set_footer(text=f"Requested by {ctx.author}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='8ball', aliases=['eightball'])
    async def eightball(self, ctx, *, question: str = None):
        """Ask the magic 8-ball a question."""
        if not question:
            await ctx.send("❌ Please ask a question!")
            return
        
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]
        
        import random
        answer = random.choice(responses)
        
        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            description=f"**Question:** {question}\n\n**Answer:** {answer}",
            color=discord.Color.purple()
        )
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BasicCommands(bot))

