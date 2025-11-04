"""
Weather Commands Cog
Handles weather-related commands using OpenWeatherMap API.
"""

import discord
from discord.ext import commands
import aiohttp
import os


class Weather(commands.Cog):
    """Weather commands."""
    
    def __init__(self, bot):
        self.bot = bot
        # Get API key and strip any whitespace
        api_key = os.getenv('WEATHER_API_KEY', '').strip()
        self.api_key = api_key if api_key else None
    
    @commands.command(name='weather')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def weather(self, ctx, *, location: str):
        """Get weather information for a location."""
        if not self.api_key:
            embed = discord.Embed(
                title="❌ Weather API Not Configured",
                description="Weather API key is not set. Please configure WEATHER_API_KEY in your .env file.\n\nGet a free API key at: https://openweathermap.org/api",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        async with ctx.typing():
            try:
                # Get weather data
                base_url = "http://api.openweathermap.org/data/2.5/weather"
                params = {
                    'q': location,
                    'appid': self.api_key,
                    'units': 'metric'  # Use metric units (Celsius)
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Extract data
                            city = data['name']
                            country = data['sys'].get('country', '')
                            temp = data['main']['temp']
                            feels_like = data['main']['feels_like']
                            humidity = data['main']['humidity']
                            pressure = data['main']['pressure']
                            description = data['weather'][0]['description'].title()
                            icon = data['weather'][0]['icon']
                            wind_speed = data['wind'].get('speed', 0)
                            visibility = data.get('visibility', 0) / 1000  # Convert to km
                            
                            embed = discord.Embed(
                                title=f"🌤️ Weather in {city}, {country}",
                                description=f"**{description}**",
                                color=discord.Color.blue()
                            )
                            
                            embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{icon}@2x.png")
                            
                            embed.add_field(name="🌡️ Temperature", value=f"{temp}°C", inline=True)
                            embed.add_field(name="🤔 Feels Like", value=f"{feels_like}°C", inline=True)
                            embed.add_field(name="💧 Humidity", value=f"{humidity}%", inline=True)
                            embed.add_field(name="🌬️ Wind Speed", value=f"{wind_speed} m/s", inline=True)
                            embed.add_field(name="📊 Pressure", value=f"{pressure} hPa", inline=True)
                            embed.add_field(name="👁️ Visibility", value=f"{visibility} km", inline=True)
                            
                            await ctx.send(embed=embed)
                        elif response.status == 401:
                            await ctx.send(f"❌ Invalid API key. Your weather API key may need activation time (10 minutes - 2 hours) or may be incorrect.\n\nCheck your key at: https://home.openweathermap.org/api_keys")
                        elif response.status == 404:
                            await ctx.send(f"❌ Location '{location}' not found. Please check the spelling.")
                        else:
                            try:
                                error_data = await response.json()
                                await ctx.send(f"❌ Error: {error_data.get('message', 'Unknown error')}")
                            except:
                                await ctx.send(f"❌ Error: HTTP {response.status}. Check your API key at https://home.openweathermap.org/api_keys")
            except aiohttp.ClientError:
                await ctx.send("❌ Error connecting to weather service. Please try again later.")
            except Exception as e:
                await ctx.send(f"❌ Error fetching weather: {str(e)}")


async def setup(bot):
    await bot.add_cog(Weather(bot))

