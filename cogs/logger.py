"""
Event Logger Cog
Logs server events (joins, leaves, message deletes, etc.) to a dedicated channel.
"""

import discord
from discord.ext import commands
from datetime import datetime, timezone


class EventLogger(commands.Cog):
    """Logs server events to a dedicated channel."""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def get_log_channel(self, guild):
        """Get or create log channel."""
        # Look for existing log channel
        for channel in guild.text_channels:
            if 'log' in channel.name.lower() or 'logs' in channel.name.lower():
                return channel
        
        # Create log channel if doesn't exist
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
            channel = await guild.create_text_channel(
                'event-logs',
                overwrites=overwrites,
                topic='Bot event logs - joins, leaves, deletions, etc.'
            )
            return channel
        except discord.Forbidden:
            return None
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Log member join."""
        log_channel = await self.get_log_channel(member.guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="✅ Member Joined",
            description=f"{member.mention} joined the server",
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="User", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log member leave."""
        log_channel = await self.get_log_channel(member.guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="👋 Member Left",
            description=f"{member.mention} left the server",
            color=discord.Color.orange(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="User", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log message deletion."""
        if message.author.bot or not message.guild:
            return
        
        log_channel = await self.get_log_channel(message.guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            description=f"Message deleted in {message.channel.mention}",
            color=discord.Color.red(),
            timestamp=datetime.now(timezone.utc)
        )
        
        content = message.content[:1024] if message.content else "*No content*"
        embed.add_field(name="Author", value=f"{message.author.mention}", inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="Content", value=content, inline=False)
        
        if message.attachments:
            embed.add_field(name="Attachments", value=f"{len(message.attachments)} file(s)", inline=True)
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Log member updates (nickname, roles)."""
        log_channel = await self.get_log_channel(before.guild)
        if not log_channel:
            return
        
        # Nickname change
        if before.display_name != after.display_name:
            embed = discord.Embed(
                title="📝 Nickname Changed",
                description=f"{after.mention} changed nickname",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="Before", value=before.display_name, inline=True)
            embed.add_field(name="After", value=after.display_name, inline=True)
            
            try:
                await log_channel.send(embed=embed)
            except:
                pass
        
        # Role change
        if before.roles != after.roles:
            added_roles = [r for r in after.roles if r not in before.roles]
            removed_roles = [r for r in before.roles if r not in after.roles]
            
            if added_roles or removed_roles:
                embed = discord.Embed(
                    title="🎭 Roles Updated",
                    description=f"{after.mention}'s roles changed",
                    color=discord.Color.purple(),
                    timestamp=datetime.now(timezone.utc)
                )
                
                if added_roles:
                    embed.add_field(
                        name="➕ Added",
                        value=", ".join([r.mention for r in added_roles]) or "None",
                        inline=False
                    )
                
                if removed_roles:
                    embed.add_field(
                        name="➖ Removed",
                        value=", ".join([r.mention for r in removed_roles]) or "None",
                        inline=False
                    )
                
                try:
                    await log_channel.send(embed=embed)
                except:
                    pass
    
    @commands.command(name='setlogchannel', aliases=['setlogs'])
    @commands.has_permissions(manage_channels=True)
    async def setlogchannel(self, ctx, channel: discord.TextChannel = None):
        """Set the log channel. Usage: !setlogchannel [channel]"""
        if channel:
            log_channel = channel
        else:
            log_channel = await self.get_log_channel(ctx.guild)
            if not log_channel:
                log_channel = await ctx.guild.create_text_channel('event-logs')
        
        embed = discord.Embed(
            title="✅ Log Channel Set",
            description=f"Event logs will be sent to {log_channel.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(EventLogger(bot))

