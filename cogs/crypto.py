"""
Crypto Commands Cog
Fetch cryptocurrency prices and information.
"""

import discord
from discord.ext import commands
import aiohttp
from datetime import datetime, timezone


class Crypto(commands.Cog):
    """Cryptocurrency commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "https://api.coingecko.com/api/v3"
    
    @commands.command(name='crypto', aliases=['price', 'btc', 'bitcoin'])
    # Removed duplicate 'crypto' from aliases to fix CommandRegistrationError
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def crypto(self, ctx, *, coin: str = 'bitcoin'):
        """Get cryptocurrency price. Usage: !crypto bitcoin or !crypto ethereum"""
        async with ctx.typing():
            try:
                # Normalize coin name
                coin_id = coin.lower().replace(' ', '-')
                
                # Try common aliases
                coin_aliases = {
                    'btc': 'bitcoin',
                    'eth': 'ethereum',
                    'doge': 'dogecoin',
                    'ada': 'cardano',
                    'sol': 'solana',
                    'xrp': 'ripple',
                    'matic': 'polygon',
                    'bnb': 'binancecoin',
                    'usdt': 'tether',
                    'usdc': 'usd-coin'
                }
                
                if coin_id in coin_aliases:
                    coin_id = coin_aliases[coin_id]
                
                async with aiohttp.ClientSession() as session:
                    url = f"{self.api_url}/simple/price"
                    params = {
                        'ids': coin_id,
                        'vs_currencies': 'usd',
                        'include_24hr_change': 'true',
                        'include_market_cap': 'true'
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if coin_id not in data:
                                # Try to search for coin
                                search_url = f"{self.api_url}/search"
                                async with session.get(search_url, params={'query': coin}) as search_resp:
                                    if search_resp.status == 200:
                                        search_data = await search_resp.json()
                                        coins = search_data.get('coins', [])[:5]
                                        
                                        if coins:
                                            embed = discord.Embed(
                                                title="❓ Coin Not Found",
                                                description=f"'{coin}' not found. Did you mean:",
                                                color=discord.Color.orange()
                                            )
                                            suggestions = []
                                            for coin_info in coins:
                                                name = coin_info.get('name', 'Unknown')
                                                suggestions.append(f"• {name}")
                                            embed.description += "\n\n" + "\n".join(suggestions[:5])
                                            await ctx.send(embed=embed)
                                            return
                                    
                                    await ctx.send(f"❌ Cryptocurrency '{coin}' not found. Try: bitcoin, ethereum, dogecoin, etc.")
                                    return
                            
                            coin_data = data[coin_id]
                            price = coin_data.get('usd', 0)
                            change_24h = coin_data.get('usd_24h_change', 0)
                            market_cap = coin_data.get('usd_market_cap', 0)
                            
                            # Format numbers
                            if price < 1:
                                price_str = f"${price:.6f}"
                            else:
                                price_str = f"${price:,.2f}"
                            
                            market_cap_str = f"${market_cap:,.0f}" if market_cap else "N/A"
                            
                            # Color based on 24h change
                            color = discord.Color.green() if change_24h >= 0 else discord.Color.red()
                            
                            embed = discord.Embed(
                                title=f"💰 {coin_id.title()} Price",
                                color=color,
                                timestamp=datetime.now(timezone.utc)
                            )
                            
                            embed.add_field(name="💵 Price", value=price_str, inline=True)
                            embed.add_field(name="📈 24h Change", value=f"{change_24h:+.2f}%", inline=True)
                            embed.add_field(name="💼 Market Cap", value=market_cap_str, inline=True)
                            
                            # Emoji based on change
                            emoji = "📈" if change_24h >= 0 else "📉"
                            embed.set_footer(text=f"{emoji} CoinGecko API")
                            
                            await ctx.send(embed=embed)
                        else:
                            await ctx.send("❌ Could not fetch cryptocurrency data. Try again later.")
            except aiohttp.ClientError:
                await ctx.send("❌ Error connecting to crypto API. Try again later.")
            except Exception as e:
                await ctx.send(f"❌ Error: {str(e)}")
    
    @commands.command(name='cryptotop', aliases=['topcrypto'])
    async def cryptotop(self, ctx, limit: int = 10):
        """Get top cryptocurrencies. Usage: !cryptotop [number]"""
        if limit < 1 or limit > 25:
            await ctx.send("❌ Please specify a number between 1 and 25.")
            return
        
        async with ctx.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"{self.api_url}/coins/markets"
                    params = {
                        'vs_currency': 'usd',
                        'order': 'market_cap_desc',
                        'per_page': limit,
                        'page': 1
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            embed = discord.Embed(
                                title=f"🏆 Top {limit} Cryptocurrencies",
                                color=discord.Color.gold()
                            )
                            
                            top_list = []
                            for i, coin in enumerate(data, 1):
                                name = coin.get('name', 'Unknown')
                                symbol = coin.get('symbol', '').upper()
                                price = coin.get('current_price', 0)
                                change = coin.get('price_change_percentage_24h', 0)
                                
                                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                                price_str = f"${price:,.2f}" if price >= 1 else f"${price:.6f}"
                                change_str = f"{change:+.2f}%"
                                
                                top_list.append(f"{emoji} **{name}** ({symbol}) - {price_str} ({change_str})")
                            
                            embed.description = "\n".join(top_list[:limit])
                            embed.set_footer(text="CoinGecko API")
                            
                            await ctx.send(embed=embed)
                        else:
                            await ctx.send("❌ Could not fetch top cryptocurrencies.")
            except Exception as e:
                await ctx.send(f"❌ Error: {str(e)}")


async def setup(bot):
    await bot.add_cog(Crypto(bot))

