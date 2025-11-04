"""
Moderation Commands Cog
Handles moderation commands like kick, ban, timeout, warn, purge.
"""

import discord
from discord.ext import commands
from datetime import timedelta
import json
from pathlib import Path


class Moderation(commands.Cog):
    """Moderation commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
    
    def load_warnings(self, guild_id):
        """Load warnings for a guild."""
        filepath = self.data_dir / f'warnings_{guild_id}.json'
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_warnings(self, guild_id, warnings):
        """Save warnings for a guild."""
        filepath = self.data_dir / f'warnings_{guild_id}.json'
        with open(filepath, 'w') as f:
            json.dump(warnings, f, indent=2)
    
    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kick a member from the server."""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot kick someone with equal or higher roles.")
            return
        
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send("❌ I cannot kick someone with equal or higher roles than me.")
            return
        
        try:
            await member.kick(reason=f"Kicked by {ctx.author}: {reason}")
            
            embed = discord.Embed(
                title="✅ Member Kicked",
                description=f"{member.mention} has been kicked from the server.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick this member.")
        except Exception as e:
            await ctx.send(f"❌ Error kicking member: {str(e)}")
    
    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Ban a member from the server."""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot ban someone with equal or higher roles.")
            return
        
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send("❌ I cannot ban someone with equal or higher roles than me.")
            return
        
        try:
            await member.ban(reason=f"Banned by {ctx.author}: {reason}")
            
            embed = discord.Embed(
                title="✅ Member Banned",
                description=f"{member.mention} has been banned from the server.",
                color=discord.Color.red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban this member.")
        except Exception as e:
            await ctx.send(f"❌ Error banning member: {str(e)}")
    
    @commands.command(name='timeout', aliases=['mute', 'tempban'])
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: str, *, reason="No reason provided"):
        """Timeout a member (mute them temporarily)."""
        from utils.helpers import parse_duration
        
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot timeout someone with equal or higher roles.")
            return
        
        seconds = parse_duration(duration)
        if not seconds or seconds < 1:
            await ctx.send("❌ Invalid duration format. Use: 1h, 30m, 5s, etc.")
            return
        
        if seconds > 604800:  # 7 days max
            await ctx.send("❌ Maximum timeout duration is 7 days.")
            return
        
        try:
            timeout_duration = timedelta(seconds=seconds)
            await member.timeout(timeout_duration, reason=f"Timed out by {ctx.author}: {reason}")
            
            embed = discord.Embed(
                title="✅ Member Timed Out",
                description=f"{member.mention} has been timed out.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Duration", value=duration, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to timeout this member.")
        except Exception as e:
            await ctx.send(f"❌ Error timing out member: {str(e)}")
    
    @commands.command(name='untimeout', aliases=['unmute'])
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Remove timeout from a member."""
        try:
            await member.timeout(None, reason=f"Untimed out by {ctx.author}: {reason}")
            
            embed = discord.Embed(
                title="✅ Timeout Removed",
                description=f"Timeout removed from {member.mention}.",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to remove timeout from this member.")
        except Exception as e:
            await ctx.send(f"❌ Error removing timeout: {str(e)}")
    
    @commands.command(name='purge', aliases=['clear', 'delete'])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = 10):
        """Delete multiple messages at once."""
        if amount < 1 or amount > 100:
            await ctx.send("❌ Please specify a number between 1 and 100.")
            return
        
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include command message
            
            embed = discord.Embed(
                title="✅ Messages Purged",
                description=f"Deleted {len(deleted) - 1} message(s).",
                color=discord.Color.green()
            )
            
            msg = await ctx.send(embed=embed)
            await msg.delete(delay=5)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to delete messages.")
        except Exception as e:
            await ctx.send(f"❌ Error purging messages: {str(e)}")
    
    @commands.command(name='warn')
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Warn a member."""
        warnings = self.load_warnings(ctx.guild.id)
        
        if str(member.id) not in warnings:
            warnings[str(member.id)] = []
        
        warning = {
            'reason': reason,
            'moderator': str(ctx.author),
            'timestamp': str(ctx.message.created_at)
        }
        
        warnings[str(member.id)].append(warning)
        self.save_warnings(ctx.guild.id, warnings)
        
        warn_count = len(warnings[str(member.id)])
        
        embed = discord.Embed(
            title="⚠️ Warning Issued",
            description=f"{member.mention} has been warned.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Total Warnings", value=warn_count, inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        
        await ctx.send(embed=embed)
        
        # DM the member
        try:
            dm_embed = discord.Embed(
                title="⚠️ You have been warned",
                description=f"You received a warning in {ctx.guild.name}",
                color=discord.Color.orange()
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Total Warnings", value=warn_count, inline=True)
            await member.send(embed=dm_embed)
        except:
            pass  # User has DMs disabled
    
    @commands.command(name='warnings', aliases=['warns'])
    async def warnings(self, ctx, member: discord.Member = None):
        """View warnings for a member."""
        member = member or ctx.author
        
        warnings = self.load_warnings(ctx.guild.id)
        user_warnings = warnings.get(str(member.id), [])
        
        if not user_warnings:
            await ctx.send(f"✅ {member.mention} has no warnings.")
            return
        
        embed = discord.Embed(
            title=f"⚠️ Warnings for {member.display_name}",
            description=f"Total: {len(user_warnings)}",
            color=discord.Color.orange()
        )
        
        for i, warning in enumerate(user_warnings[-5:], 1):  # Show last 5
            embed.add_field(
                name=f"Warning #{i}",
                value=f"**Reason:** {warning.get('reason', 'N/A')}\n**By:** {warning.get('moderator', 'Unknown')}\n**Date:** {warning.get('timestamp', 'Unknown')}",
                inline=False
            )
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))

