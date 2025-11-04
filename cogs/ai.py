"""
AI Commands Cog
Handles AI-powered responses using Groq API.
"""

import discord
from discord.ext import commands
import os
import aiohttp
import json

class AI(commands.Cog):
    """AI-powered commands using Groq API."""
    
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('GROQ_API_KEY')
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        # Updated models - using current available models
        self.available_models = [
            'llama-3.1-8b-instant',  # Fast and efficient
            'llama-3.1-70b-versatile',  # More powerful
            'mixtral-8x7b-32768',  # Good balance
            'gemma2-9b-it'  # Alternative option
        ]
        self.current_model = 'llama-3.1-8b-instant'  # Default model
        print(f"Groq API Key loaded: {'Yes' if self.api_key else 'No'}")
    
    async def check_api_key(self):
        """Check if the Groq API key is valid."""
        if not self.api_key:
            return False, "❌ Groq API key is not set in .env file"
            
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                test_payload = {
                    'model': self.current_model,  # Use current model
                    'messages': [{'role': 'user', 'content': 'Say "API test successful"'}],
                    'max_tokens': 10
                }
                
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=test_payload,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        return True, f"✅ Groq API key is valid and working! (Model: {self.current_model})"
                    elif response.status == 401:
                        return False, "❌ Invalid API key. Please check your GROQ_API_KEY in .env"
                    elif response.status == 404:
                        # Model might be deprecated, try another one
                        await self.rotate_model()
                        return False, "❌ Model issue. Trying alternative model..."
                    else:
                        error = await response.json()
                        return False, f"❌ API Error: {error.get('error', {}).get('message', 'Unknown error')}"
                        
        except aiohttp.ClientError as e:
            return False, f"❌ Connection error: {str(e)}"
        except Exception as e:
            return False, f"❌ Error: {str(e)}"

    async def rotate_model(self):
        """Rotate to the next available model if current one fails."""
        current_index = self.available_models.index(self.current_model)
        next_index = (current_index + 1) % len(self.available_models)
        self.current_model = self.available_models[next_index]
        print(f"Rotated to model: {self.current_model}")

    @commands.command(name='checkkey')
    async def check_key(self, ctx):
        """Check if the Groq API key is working."""
        is_valid, message = await self.check_api_key()
        embed = discord.Embed(
            title="🔑 Groq API Key Status",
            description=message,
            color=discord.Color.blue() if is_valid else discord.Color.red()
        )
        
        if not is_valid:
            embed.add_field(
                name="How to fix:",
                value="1. Get an API key from https://console.groq.com/keys\n"
                      "2. Add it to your .env file: `GROQ_API_KEY=your_key_here`\n"
                      "3. Restart your bot",
                inline=False
            )
        else:
            embed.add_field(
                name="Available Models",
                value="\n".join([f"• {model}" for model in self.available_models]),
                inline=False
            )
            embed.add_field(
                name="Current Model",
                value=self.current_model,
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    async def get_ai_response(self, prompt: str) -> str:
        """Get response from Groq API."""
        if not self.api_key:
            return "❌ Error: Groq API key is not configured."
            
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.current_model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 1000,
            'temperature': 0.7
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    elif response.status == 404:
                        # Model deprecated, rotate and retry
                        await self.rotate_model()
                        return await self.get_ai_response(prompt)  # Retry with new model
                    else:
                        error = await response.json()
                        return f"❌ API Error: {error.get('error', {}).get('message', 'Unknown error')}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @commands.command(name='ask', aliases=['question', 'ai'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ask(self, ctx, *, question: str):
        """Ask the AI a question."""
        is_valid, _ = await self.check_api_key()
        if not is_valid:
            await ctx.send("❌ Groq API key is not properly configured. Use `!checkkey` for details.")
            return
            
        async with ctx.typing():
            response = await self.get_ai_response(question)
            
            # Create embed for better formatting
            if not response.startswith("❌"):
                embed = discord.Embed(
                    title="🤖 AI Response",
                    description=response[:4096],  # Discord embed limit
                    color=discord.Color.green()
                )
                embed.set_footer(text=f"Model: {self.current_model} | Asked by {ctx.author.display_name}")
                await ctx.send(embed=embed)
            else:
                # Send error as regular message
                if len(response) > 2000:
                    chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                    for chunk in chunks:
                        await ctx.send(chunk)
                else:
                    await ctx.send(response)
    
    @commands.command(name='model')
    async def change_model(self, ctx, model_name: str = None):
        """Change or view the current AI model."""
        if model_name:
            if model_name in self.available_models:
                self.current_model = model_name
                embed = discord.Embed(
                    title="🔧 Model Changed",
                    description=f"Switched to: **{model_name}**",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="❌ Invalid Model",
                    description=f"Available models:\n" + "\n".join([f"• {model}" for model in self.available_models]),
                    color=discord.Color.red()
                )
        else:
            embed = discord.Embed(
                title="🔧 Current Model",
                description=f"**Current:** {self.current_model}\n\n**Available:**\n" + "\n".join([f"• {model}" for model in self.available_models]),
                color=discord.Color.blue()
            )
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Check API key when bot starts."""
        is_valid, message = await self.check_api_key()
        if is_valid:
            print(f"✅ Groq API key is valid and working! (Model: {self.current_model})")
        else:
            print(f"⚠️ {message}")

async def setup(bot):
    await bot.add_cog(AI(bot))