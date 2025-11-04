"""
Statistics Cog
Tracks and displays user statistics and server activity.
"""

import discord
from discord.ext import commands
from datetime import datetime, timezone
import json
from pathlib import Path
from utils.helpers import load_json, save_json


class Statistics(commands.Cog):
    """User and server statistics tracking."""
    
    def __init__(self, bot):
        self.bot = bot
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.stats_file = self.data_dir / 'user_stats.json'
        self.stats = load_json('user_stats.json')
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Track message statistics."""
        if message.author.bot or not message.guild:
            return
        
        guild_id = str(message.guild.id)
        user_id = str(message.author.id)
        
        if guild_id not in self.stats:
            self.stats[guild_id] = {}
        
        if user_id not in self.stats[guild_id]:
            self.stats[guild_id][user_id] = {
                'messages': 0,
                'commands_used': 0,
                'first_seen': datetime.now(timezone.utc).isoformat(),
                'last_seen': datetime.now(timezone.utc).isoformat()
            }
        
        self.stats[guild_id][user_id]['messages'] += 1
        self.stats[guild_id][user_id]['last_seen'] = datetime.now(timezone.utc).isoformat()
        
        # Check if it's a command
        if message.content.startswith(self.bot.command_prefix):
            self.stats[guild_id][user_id]['commands_used'] += 1
        
        # Save periodically (every 10 messages to reduce I/O)
        if self.stats[guild_id][user_id]['messages'] % 10 == 0:
            save_json('user_stats.json', self.stats)
    
    @commands.command(name='stats', aliases=['statistics', 'userstats'])
    async def stats(self, ctx, member: discord.Member = None):
        """View user statistics."""
        member = member or ctx.author
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
        
        if guild_id not in self.stats or user_id not in self.stats[guild_id]:
            await ctx.send(f"📊 {member.mention} has no statistics yet.")
            return
        
        user_stats = self.stats[guild_id][user_id]
        
        # Calculate activity level
        messages = user_stats.get('messages', 0)
        commands = user_stats.get('commands_used', 0)
        
        if messages < 10:
            activity = "🌱 New"
        elif messages < 100:
            activity = "📝 Active"
        elif messages < 500:
            activity = "🔥 Very Active"
        elif messages < 1000:
            activity = "⭐ Super Active"
        else:
            activity = "💎 Legendary"
        
        embed = discord.Embed(
            title=f"📊 Statistics for {member.display_name}",
            color=member.color if member.color != discord.Color.default() else discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        embed.add_field(name="💬 Messages Sent", value=user_stats.get('messages', 0), inline=True)
        embed.add_field(name="⚡ Commands Used", value=user_stats.get('commands_used', 0), inline=True)
        embed.add_field(name="📈 Activity Level", value=activity, inline=True)
        
        now = datetime.now(timezone.utc)
        first_seen_str = user_stats.get('first_seen', now.isoformat())
        last_seen_str = user_stats.get('last_seen', now.isoformat())
        
        # Parse datetime strings, handling both with and without timezone
        try:
            first_seen = datetime.fromisoformat(first_seen_str.replace('Z', '+00:00'))
            if first_seen.tzinfo is None:
                first_seen = first_seen.replace(tzinfo=timezone.utc)
        except:
            first_seen = now
        
        try:
            last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=timezone.utc)
        except:
            last_seen = now
        
        embed.add_field(name="📅 First Seen", value=first_seen.strftime("%Y-%m-%d %H:%M"), inline=True)
        embed.add_field(name="🕐 Last Seen", value=last_seen.strftime("%Y-%m-%d %H:%M"), inline=True)
        
        # Calculate account age - make both timezone-aware
        account_created = member.created_at
        if account_created.tzinfo is None:
            account_created = account_created.replace(tzinfo=timezone.utc)
        account_age = (now - account_created).days
        embed.add_field(name="🗓️ Account Age", value=f"{account_age} days", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='leaderboard', aliases=['lb', 'top'])
    async def leaderboard(self, ctx, metric: str = 'messages'):
        """View server leaderboard."""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.stats or not self.stats[guild_id]:
            await ctx.send("📊 No statistics available yet.")
            return
        
        # Sort by metric
        metric_key = 'messages' if metric.lower() in ['messages', 'msg', 'm'] else 'commands_used'
        
        sorted_users = sorted(
            self.stats[guild_id].items(),
            key=lambda x: x[1].get(metric_key, 0),
            reverse=True
        )[:10]
        
        embed = discord.Embed(
            title=f"🏆 Leaderboard - {metric_key.title()}",
            description="Top 10 users",
            color=discord.Color.gold()
        )
        
        leaderboard_text = []
        for i, (user_id, stats) in enumerate(sorted_users, 1):
            user = ctx.guild.get_member(int(user_id))
            if user:
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                value = stats.get(metric_key, 0)
                leaderboard_text.append(f"{emoji} {user.mention} - {value:,}")
        
        embed.description = "\n".join(leaderboard_text) if leaderboard_text else "No data available"
        
        await ctx.send(embed=embed)
    
    def cog_unload(self):
        """Save statistics when cog is unloaded."""
        save_json('user_stats.json', self.stats)


async def setup(bot):
    await bot.add_cog(Statistics(bot))

