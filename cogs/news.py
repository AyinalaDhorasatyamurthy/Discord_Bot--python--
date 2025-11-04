"""
News Commands Cog
Fetch news from various sources using NewsAPI.
"""

import discord
from discord.ext import commands
import aiohttp
import os
from datetime import datetime, timezone


class News(commands.Cog):
    """News commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('NEWS_API_KEY')
        self.api_url = "https://newsapi.org/v2"
    
    @commands.command(name='news')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def news(self, ctx, category: str = 'general', limit: int = 5):
        """Get latest news. Usage: !news [category] [limit]
        Categories: general, technology, business, sports, health, science
        """
        if not self.api_key:
            embed = discord.Embed(
                title="❌ News API Not Configured",
                description="News API key is not set. Get a free key at: https://newsapi.org/register\n\nAdd NEWS_API_KEY to your .env file.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if limit < 1 or limit > 10:
            limit = 5
        
        category_map = {
            'tech': 'technology',
            'business': 'business',
            'sports': 'sports',
            'health': 'health',
            'science': 'science',
            'general': 'general'
        }
        
        category = category_map.get(category.lower(), 'general')
        
        async with ctx.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {'X-Api-Key': self.api_key}
                    url = f"{self.api_url}/top-headlines"
                    params = {
                        'category': category,
                        'country': 'us',  # Can be changed to other countries
                        'pageSize': limit
                    }
                    
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            articles = data.get('articles', [])
                            
                            if not articles:
                                await ctx.send(f"❌ No news found for category '{category}'.")
                                return
                            
                            embed = discord.Embed(
                                title=f"📰 Latest {category.title()} News",
                                color=discord.Color.blue(),
                                timestamp=datetime.now(timezone.utc)
                            )
                            
                            for i, article in enumerate(articles[:limit], 1):
                                title = article.get('title', 'No title')[:256]
                                url = article.get('url', '#')
                                source = article.get('source', {}).get('name', 'Unknown')
                                
                                embed.add_field(
                                    name=f"{i}. {title}",
                                    value=f"[Read more]({url}) | Source: {source}",
                                    inline=False
                                )
                            
                            embed.set_footer(text=f"NewsAPI | {len(articles)} article(s)")
                            await ctx.send(embed=embed)
                        elif response.status == 401:
                            await ctx.send("❌ Invalid News API key. Check your NEWS_API_KEY.")
                        else:
                            await ctx.send("❌ Could not fetch news. Try again later.")
            except aiohttp.ClientError:
                await ctx.send("❌ Error connecting to news service. Try again later.")
            except Exception as e:
                await ctx.send(f"❌ Error: {str(e)}")
    
    @commands.command(name='newssearch', aliases=['searchnews'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def newssearch(self, ctx, *, query: str):
        """Search for news articles. Usage: !newssearch Python"""
        if not self.api_key:
            await ctx.send("❌ News API key not configured. Get one at: https://newsapi.org/register")
            return
        
        async with ctx.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {'X-Api-Key': self.api_key}
                    url = f"{self.api_url}/everything"
                    params = {
                        'q': query,
                        'sortBy': 'publishedAt',
                        'pageSize': 5,
                        'language': 'en'
                    }
                    
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            articles = data.get('articles', [])
                            
                            if not articles:
                                await ctx.send(f"❌ No articles found for '{query}'.")
                                return
                            
                            embed = discord.Embed(
                                title=f"🔍 News Search: {query}",
                                color=discord.Color.blue()
                            )
                            
                            for i, article in enumerate(articles, 1):
                                title = article.get('title', 'No title')[:256]
                                url = article.get('url', '#')
                                source = article.get('source', {}).get('name', 'Unknown')
                                published = article.get('publishedAt', '')[:10]
                                
                                embed.add_field(
                                    name=f"{i}. {title}",
                                    value=f"[Read more]({url})\nSource: {source} | {published}",
                                    inline=False
                                )
                            
                            await ctx.send(embed=embed)
                        else:
                            await ctx.send("❌ Could not search news. Try again later.")
            except Exception as e:
                await ctx.send(f"❌ Error: {str(e)}")


async def setup(bot):
    await bot.add_cog(News(bot))

