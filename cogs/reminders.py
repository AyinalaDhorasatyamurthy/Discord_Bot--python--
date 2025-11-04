"""
Reminders Cog
Handles reminder functionality for users.
"""

import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import json
from utils.helpers import parse_duration


class Reminders(commands.Cog):
    """Reminder commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.reminders_file = self.data_dir / 'reminders.json'
        self.reminders = self.load_reminders()
        self.bot.loop.create_task(self.check_reminders())
    
    def load_reminders(self):
        """Load reminders from file."""
        if self.reminders_file.exists():
            try:
                with open(self.reminders_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_reminders(self):
        """Save reminders to file."""
        with open(self.reminders_file, 'w') as f:
            json.dump(self.reminders, f, indent=2)
    
    async def check_reminders(self):
        """Background task to check and send reminders."""
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            try:
                current_time = datetime.utcnow()
                reminders_to_remove = []
                
                for reminder_id, reminder_data in self.reminders.items():
                    remind_time = datetime.fromisoformat(reminder_data['remind_at'])
                    
                    if current_time >= remind_time:
                        # Send reminder
                        try:
                            user = self.bot.get_user(reminder_data['user_id'])
                            if user:
                                embed = discord.Embed(
                                    title="⏰ Reminder",
                                    description=reminder_data['message'],
                                    color=discord.Color.blue(),
                                    timestamp=datetime.utcnow()
                                )
                                await user.send(embed=embed)
                            else:
                                # Try to get from guild
                                guild = self.bot.get_guild(reminder_data.get('guild_id', 0))
                                if guild:
                                    member = guild.get_member(reminder_data['user_id'])
                                    if member:
                                        embed = discord.Embed(
                                            title="⏰ Reminder",
                                            description=reminder_data['message'],
                                            color=discord.Color.blue(),
                                            timestamp=datetime.utcnow()
                                        )
                                        await member.send(embed=embed)
                        except discord.Forbidden:
                            pass  # User has DMs disabled
                        except Exception as e:
                            print(f"Error sending reminder: {e}")
                        
                        reminders_to_remove.append(reminder_id)
                
                # Remove sent reminders
                for reminder_id in reminders_to_remove:
                    del self.reminders[reminder_id]
                
                if reminders_to_remove:
                    self.save_reminders()
                
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"Error in reminder check: {e}")
                await asyncio.sleep(60)
    
    @commands.command(name='remind', aliases=['reminder', 'timer'])
    async def remind(self, ctx, duration: str, *, message: str):
        """Set a reminder. Usage: !remind 1h 30m check email"""
        seconds = parse_duration(duration)
        
        if not seconds or seconds < 1:
            await ctx.send("❌ Invalid duration format. Use: 1h, 30m, 5s, etc.\nExample: `!remind 1h 30m check email`")
            return
        
        if seconds > 2592000:  # 30 days max
            await ctx.send("❌ Maximum reminder duration is 30 days.")
            return
        
        remind_time = datetime.utcnow() + timedelta(seconds=seconds)
        reminder_id = f"{ctx.author.id}_{datetime.utcnow().timestamp()}"
        
        self.reminders[reminder_id] = {
            'user_id': ctx.author.id,
            'guild_id': ctx.guild.id if ctx.guild else 0,
            'message': message,
            'remind_at': remind_time.isoformat(),
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.save_reminders()
        
        embed = discord.Embed(
            title="✅ Reminder Set",
            description=f"I'll remind you in {duration}",
            color=discord.Color.green()
        )
        embed.add_field(name="Reminder", value=message, inline=False)
        embed.add_field(name="Time", value=remind_time.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='reminders', aliases=['myreminders'])
    async def reminders(self, ctx):
        """View your active reminders."""
        user_reminders = [
            (rid, rdata) for rid, rdata in self.reminders.items()
            if rdata['user_id'] == ctx.author.id
        ]
        
        if not user_reminders:
            await ctx.send("✅ You have no active reminders.")
            return
        
        embed = discord.Embed(
            title=f"⏰ Your Active Reminders",
            description=f"You have {len(user_reminders)} active reminder(s)",
            color=discord.Color.blue()
        )
        
        for i, (rid, rdata) in enumerate(user_reminders[:10], 1):  # Show first 10
            remind_time = datetime.fromisoformat(rdata['remind_at'])
            time_str = remind_time.strftime("%Y-%m-%d %H:%M:%S UTC")
            
            embed.add_field(
                name=f"Reminder #{i}",
                value=f"**Message:** {rdata['message']}\n**Time:** {time_str}",
                inline=False
            )
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Reminders(bot))

