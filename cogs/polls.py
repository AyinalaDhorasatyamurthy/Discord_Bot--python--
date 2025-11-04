"""
Polls and Voting Cog
Create interactive polls with buttons and reactions.
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio


class Polls(commands.Cog):
    """Poll and voting commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {}  # Store active polls
    
    @commands.command(name='poll', aliases=['vote'])
    async def poll(self, ctx, question: str, *, options: str = None):
        """Create a poll. Usage: !poll "Question?" Option1 Option2 Option3"""
        if not options:
            # Quick yes/no poll
            embed = discord.Embed(
                title=f"📊 Poll: {question}",
                description="React to vote!",
                color=discord.Color.blue()
            )
            embed.add_field(name="✅ Yes", value="React with ✅", inline=True)
            embed.add_field(name="❌ No", value="React with ❌", inline=True)
            
            msg = await ctx.send(embed=embed)
            await msg.add_reaction('✅')
            await msg.add_reaction('❌')
        else:
            # Multi-option poll
            option_list = options.split()
            if len(option_list) < 2:
                await ctx.send("❌ Please provide at least 2 options!")
                return
            
            if len(option_list) > 10:
                await ctx.send("❌ Maximum 10 options allowed!")
                return
            
            # Use number emojis
            number_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
            
            embed = discord.Embed(
                title=f"📊 Poll: {question}",
                description="React to vote!",
                color=discord.Color.blue()
            )
            
            for i, option in enumerate(option_list[:10], 1):
                embed.add_field(name=f"{number_emojis[i-1]} {option}", value=f"React with {number_emojis[i-1]}", inline=False)
            
            embed.set_footer(text=f"Poll created by {ctx.author.display_name}")
            
            msg = await ctx.send(embed=embed)
            
            # Add reactions
            for i in range(len(option_list)):
                await msg.add_reaction(number_emojis[i])
    
    @commands.command(name='quickpoll', aliases=['qp'])
    async def quickpoll(self, ctx, *, question: str):
        """Quick yes/no poll. Usage: !quickpoll Is Python the best?"""
        embed = discord.Embed(
            title=f"📊 Quick Poll",
            description=f"**{question}**",
            color=discord.Color.green()
        )
        embed.add_field(name="✅ Yes", value="Click button below", inline=True)
        embed.add_field(name="❌ No", value="Click button below", inline=True)
        embed.set_footer(text=f"Poll by {ctx.author.display_name}")
        
        # Create buttons
        view = PollView(question)
        await ctx.send(embed=embed, view=view)


class PollView(discord.ui.View):
    """Interactive poll view with buttons."""
    
    def __init__(self, question: str, timeout: float = 86400):  # 24 hour timeout
        super().__init__(timeout=timeout)
        self.question = question
        self.votes = {'yes': [], 'no': []}
    
    @discord.ui.button(label='✅ Yes', style=discord.ButtonStyle.green, emoji='✅')
    async def vote_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        
        # Remove from no if voted
        if user_id in self.votes['no']:
            self.votes['no'].remove(user_id)
        
        # Add to yes
        if user_id not in self.votes['yes']:
            self.votes['yes'].append(user_id)
        
        await interaction.response.send_message(f"✅ You voted **Yes**!", ephemeral=True)
        await self.update_embed(interaction)
    
    @discord.ui.button(label='❌ No', style=discord.ButtonStyle.red, emoji='❌')
    async def vote_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        
        # Remove from yes if voted
        if user_id in self.votes['yes']:
            self.votes['yes'].remove(user_id)
        
        # Add to no
        if user_id not in self.votes['no']:
            self.votes['no'].append(user_id)
        
        await interaction.response.send_message(f"❌ You voted **No**!", ephemeral=True)
        await self.update_embed(interaction)
    
    async def update_embed(self, interaction: discord.Interaction):
        """Update the poll embed with current votes."""
        yes_count = len(self.votes['yes'])
        no_count = len(self.votes['no'])
        total = yes_count + no_count
        
        embed = discord.Embed(
            title=f"📊 Quick Poll",
            description=f"**{self.question}**",
            color=discord.Color.green()
        )
        
        yes_bar = "█" * int(yes_count / max(total, 1) * 20) if total > 0 else ""
        no_bar = "█" * int(no_count / max(total, 1) * 20) if total > 0 else ""
        
        embed.add_field(
            name=f"✅ Yes ({yes_count})",
            value=f"{yes_bar} {yes_count} votes" if yes_bar else "No votes yet",
            inline=False
        )
        embed.add_field(
            name=f"❌ No ({no_count})",
            value=f"{no_bar} {no_count} votes" if no_bar else "No votes yet",
            inline=False
        )
        
        if total > 0:
            yes_percent = int((yes_count / total) * 100)
            no_percent = int((no_count / total) * 100)
            embed.add_field(
                name="📊 Results",
                value=f"**Yes:** {yes_percent}% | **No:** {no_percent}%",
                inline=False
            )
        
        embed.set_footer(text=f"Total votes: {total}")
        
        try:
            await interaction.message.edit(embed=embed, view=self)
        except:
            pass


async def setup(bot):
    await bot.add_cog(Polls(bot))

