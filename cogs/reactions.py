"""
Auto Reactions Cog
Automatically reacts to messages based on keywords and content.
"""

import discord
from discord.ext import commands
import random
import re


class AutoReactions(commands.Cog):
    """Automatic emoji reactions to messages."""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Keyword to emoji mappings
        self.reaction_map = {
            # Positive reactions
            'wow': ['😲', '🤯', '😱'],
            'amazing': ['✨', '🌟', '💫'],
            'awesome': ['🔥', '💯', '⭐'],
            'great': ['👍', '👏', '🎉'],
            'good': ['👍', '😊', '✅'],
            'nice': ['😊', '👍', '👌'],
            'cool': ['😎', '👌', '✨'],
            'congrats': ['🎉', '🎊', '👏'],
            'congratulations': ['🎉', '🎊', '🏆'],
            'welcome': ['👋', '🎉', '🎊'],
            'thanks': ['🙏', '💙', '😊'],
            'thank you': ['🙏', '💙'],
            
            # Emotional reactions
            'love': ['❤️', '💕', '💖'],
            'hate': ['😡', '👎'],
            'happy': ['😊', '😄', '😃'],
            'sad': ['😢', '😔', '💔'],
            'excited': ['🎉', '🔥', '✨'],
            'proud': ['👏', '🏆', '🌟'],
            
            # Question reactions
            'why': ['🤔', '💭'],
            'how': ['🤔', '💡'],
            'what': ['🤔', '❓'],
            'when': ['🤔', '📅'],
            'who': ['🤔', '👤'],
            
            # Technical reactions
            'python': ['🐍', '💻'],
            'code': ['💻', '⌨️'],
            'programming': ['💻', '🔧'],
            'bug': ['🐛', '🔧'],
            'error': ['❌', '⚠️'],
            'fixed': ['✅', '🔧'],
            'working': ['✅', '👍'],
            
            # Fun reactions
            'lol': ['😂', '🤣'],
            'haha': ['😂', '😄'],
            'funny': ['😂', '🤣'],
            'joke': ['😆', '🎭'],
        }
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Auto-react to messages based on keywords."""
        if message.author.bot or not message.guild:
            return
        
        # Don't react to commands
        if message.content.startswith(self.bot.command_prefix):
            return
        
        content_lower = message.content.lower()
        reacted = set()  # Track which emojis we've already added
        
        # Check each keyword
        for keyword, emojis in self.reaction_map.items():
            # Match whole word or at start/end of message
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, content_lower):
                # Randomly select an emoji from the list
                emoji = random.choice(emojis)
                if emoji not in reacted:
                    try:
                        await message.add_reaction(emoji)
                        reacted.add(emoji)
                        # Limit to 3 reactions per message to avoid spam
                        if len(reacted) >= 3:
                            break
                    except (discord.Forbidden, discord.HTTPException):
                        pass
        
        # Special reactions for specific content
        if not reacted:
            # React to images
            if message.attachments and any(att.content_type and 'image' in att.content_type for att in message.attachments):
                try:
                    await message.add_reaction('🖼️')
                except:
                    pass
            
            # React to links
            if 'http://' in content_lower or 'https://' in content_lower:
                try:
                    await message.add_reaction('🔗')
                except:
                    pass
            
            # React to questions
            if content_lower.endswith('?') and len(content_lower) < 100:
                try:
                    await message.add_reaction('❓')
                except:
                    pass
    
    @commands.command(name='react', aliases=['addreact'])
    @commands.has_permissions(manage_messages=True)
    async def react(self, ctx, emoji: str, *, message_id: int = None):
        """Add a reaction to a message. Usage: !react :emoji: [message_id]"""
        if message_id:
            try:
                msg = await ctx.channel.fetch_message(message_id)
                await msg.add_reaction(emoji)
                await ctx.send(f"✅ Added {emoji} reaction!")
            except discord.NotFound:
                await ctx.send("❌ Message not found.")
            except discord.HTTPException:
                await ctx.send("❌ Invalid emoji or couldn't add reaction.")
        else:
            if ctx.message.reference and ctx.message.reference.resolved:
                msg = ctx.message.reference.resolved
                try:
                    await msg.add_reaction(emoji)
                    await ctx.send(f"✅ Added {emoji} reaction!")
                except:
                    await ctx.send("❌ Couldn't add reaction.")
            else:
                await ctx.send("❌ Reply to a message or provide message ID!")


async def setup(bot):
    await bot.add_cog(AutoReactions(bot))

