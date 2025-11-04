"""
MUSIC COG - FIXED DUPLICATE MESSAGE ISSUE
"""

import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import yt_dlp
import asyncio
import os

# yt-dlp options
ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': False,
    'no_warnings': False,
    'default_search': 'ytsearch',
    'extractaudio': True,
    'audioformat': 'mp3',
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'geo_bypass': True
}

ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.voice_clients = {}
        self.current_songs = {}
        self.ffmpeg_path = 'ffmpeg.exe' if os.path.exists('ffmpeg.exe') else 'ffmpeg'
    
    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]
    
    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx, *, query):
        """Play music from YouTube"""
        if not ctx.author.voice:
            await ctx.send("❌ Join a voice channel first!")
            return
        
        voice_channel = ctx.author.voice.channel
        
        # Connect to voice
        if ctx.guild.id not in self.voice_clients:
            self.voice_clients[ctx.guild.id] = await voice_channel.connect()
        else:
            await self.voice_clients[ctx.guild.id].move_to(voice_channel)
        
        # Show searching message
        search_msg = await ctx.send("🔍 **Searching for your song...**")
        
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
                # Format query for search
                if not query.startswith(('http://', 'https://', 'www.')):
                    search_query = f"ytsearch:{query}"
                else:
                    search_query = query
                
                print(f"Searching for: {search_query}")
                
                info = ytdl.extract_info(search_query, download=False)
                
                # Handle search results
                if 'entries' in info:
                    if info['entries']:
                        video = info['entries'][0]
                    else:
                        await search_msg.delete()
                        await ctx.send("❌ No results found!")
                        return
                else:
                    video = info
                
                # Get the URL
                url = None
                if 'url' in video:
                    url = video['url']
                elif 'formats' in video:
                    for fmt in video['formats']:
                        if fmt.get('acodec') != 'none':
                            url = fmt.get('url')
                            if url:
                                break
                
                if not url:
                    await search_msg.delete()
                    await ctx.send("❌ Could not get audio URL")
                    return
                
                title = video.get('title', 'Unknown Title')
                webpage_url = video.get('webpage_url', video.get('original_url', ''))
                thumbnail = video.get('thumbnail', '')
                
                song = {
                    'url': url,
                    'title': title,
                    'webpage_url': webpage_url,
                    'thumbnail': thumbnail
                }
                
                queue = self.get_queue(ctx.guild.id)
                current_song = self.current_songs.get(ctx.guild.id)
                
                await search_msg.delete()
                
                # Check if already playing this exact song
                if current_song and current_song['url'] == song['url']:
                    embed = discord.Embed(
                        title="ℹ️ Already Playing",
                        description=f"[{title}]({webpage_url}) is currently playing!",
                        color=discord.Color.orange()
                    )
                    if thumbnail:
                        embed.set_thumbnail(url=thumbnail)
                    await ctx.send(embed=embed)
                    return
                
                # Check if song is already in queue
                is_in_queue = any(s['url'] == song['url'] for s in queue)
                if is_in_queue:
                    embed = discord.Embed(
                        title="ℹ️ Already in Queue",
                        description=f"[{title}]({webpage_url}) is already in the queue!",
                        color=discord.Color.orange()
                    )
                    if thumbnail:
                        embed.set_thumbnail(url=thumbnail)
                    await ctx.send(embed=embed)
                    return
                
                # Check if currently playing anything
                is_playing = (self.voice_clients[ctx.guild.id].is_playing() or 
                            self.voice_clients[ctx.guild.id].is_paused())
                
                if not is_playing and not queue:
                    # Case 1: First song - play immediately without adding to queue
                    self.current_songs[ctx.guild.id] = song
                    await self._play_song(ctx.guild.id, song)
                    
                    embed = discord.Embed(
                        title="▶️ Now Playing",
                        description=f"[{title}]({webpage_url})",
                        color=discord.Color.green()
                    )
                elif is_playing:
                    # Case 2: Something is already playing - add to queue
                    queue.append(song)
                    embed = discord.Embed(
                        title="🎵 Added to Queue",
                        description=f"[{title}]({webpage_url})",
                        color=discord.Color.blue()
                    )
                    embed.set_footer(text=f"Position in queue: {len(queue)}")
                else:
                    # Case 3: Queue is not empty but nothing is playing - start playing from queue
                    queue.insert(0, song)  # Add to front of queue
                    next_song = queue.pop(0)
                    self.current_songs[ctx.guild.id] = next_song
                    await self._play_song(ctx.guild.id, next_song)
                    
                    embed = discord.Embed(
                        title="▶️ Now Playing",
                        description=f"[{title}]({webpage_url})",
                        color=discord.Color.green()
                    )
                
                # Send the appropriate embed message
                if thumbnail:
                    embed.set_thumbnail(url=thumbnail)
                await ctx.send(embed=embed)
                    
        except Exception as e:
            await search_msg.delete()
            print(f"Error: {e}")
            await ctx.send(f"❌ Error: {str(e)}")
    
    async def _play_song(self, guild_id, song):
        """Internal method to play a song"""
        if guild_id not in self.voice_clients:
            return
        
        def after_playing(error):
            if error:
                print(f'Player error: {error}')
            
            # Clear current song
            if guild_id in self.current_songs:
                del self.current_songs[guild_id]
            
            # Play next song from queue
            asyncio.run_coroutine_threadsafe(self._play_next(guild_id), self.bot.loop) 
        
        try:
            # Stop any currently playing track
            if self.voice_clients[guild_id].is_playing() or self.voice_clients[guild_id].is_paused():
                self.voice_clients[guild_id].stop()
            
            # Set the current song
            self.current_songs[guild_id] = song
            
            # Create and play the audio source
            source = FFmpegPCMAudio(
                song['url'],
                executable=self.ffmpeg_path,
                **ffmpeg_opts
            )
            
            # Play the source with error handling
            def play_source():
                try:
                    self.voice_clients[guild_id].play(source, after=after_playing)
                except Exception as e:
                    print(f"Error in play_source: {e}")
                    after_playing(e)
            
            # Run the play in a thread to avoid blocking
            self.bot.loop.call_soon_threadsafe(play_source)
            
        except Exception as e:
            print(f"Playback error: {e}")
            # Clear current song on error and try next
            if guild_id in self.current_songs:
                del self.current_songs[guild_id]
            asyncio.run_coroutine_threadsafe(self._play_next(guild_id), self.bot.loop)
    
    async def _play_next(self, guild_id):
        """Internal method to play next song from queue"""
        queue = self.get_queue(guild_id)
        if queue and guild_id in self.voice_clients:
            next_song = queue.pop(0)
            self.current_songs[guild_id] = next_song
            await self._play_song(guild_id, next_song)
    
    @commands.command()
    async def skip(self, ctx):
        """Skip current song"""
        if ctx.guild.id in self.voice_clients and self.voice_clients[ctx.guild.id].is_playing():
            self.voice_clients[ctx.guild.id].stop()
            await ctx.send("⏭️ Skipped!")
        else:
            await ctx.send("❌ Nothing playing!")
    
    @commands.command()
    async def stop(self, ctx):
        """Stop music"""
        if ctx.guild.id in self.voice_clients:
            self.queues[ctx.guild.id] = []
            self.current_songs[ctx.guild.id] = None
            self.voice_clients[ctx.guild.id].stop()
            await self.voice_clients[ctx.guild.id].disconnect()
            del self.voice_clients[ctx.guild.id]
            await ctx.send("⏹️ Stopped!")
        else:
            await ctx.send("❌ Not playing!")
    
    @commands.command()
    async def pause(self, ctx):
        """Pause the current song"""
        if ctx.guild.id in self.voice_clients:
            if self.voice_clients[ctx.guild.id].is_playing():
                self.voice_clients[ctx.guild.id].pause()
                await ctx.send("⏸️ Paused!")
            elif self.voice_clients[ctx.guild.id].is_paused():
                await ctx.send("⏸️ Already paused!")
            else:
                await ctx.send("❌ Nothing is playing!")
        else:
            await ctx.send("❌ I'm not in a voice channel!")
    
    @commands.command()
    async def resume(self, ctx):
        """Resume the paused song"""
        if ctx.guild.id in self.voice_clients:
            if self.voice_clients[ctx.guild.id].is_paused():
                self.voice_clients[ctx.guild.id].resume()
                await ctx.send("▶️ Resumed!")
            elif self.voice_clients[ctx.guild.id].is_playing():
                await ctx.send("▶️ Already playing!")
            else:
                await ctx.send("❌ Nothing is paused!")
        else:
            await ctx.send("❌ I'm not in a voice channel!")
    
    @commands.command()
    async def queue(self, ctx):
        """Show current queue"""
        queue = self.get_queue(ctx.guild.id)
        current_song = self.current_songs.get(ctx.guild.id)
        
        embed = discord.Embed(title="🎵 Music Queue", color=discord.Color.blue())
        
        if current_song:
            embed.add_field(
                name="▶️ Now Playing",
                value=f"[{current_song['title']}]({current_song['webpage_url']})",
                inline=False
            )
        
        if queue:
            queue_list = []
            for i, song in enumerate(queue[:10], 1):
                queue_list.append(f"{i}. [{song['title']}]({song['webpage_url']})")
            
            embed.add_field(
                name="Up Next",
                value="\n".join(queue_list),
                inline=False
            )
        else:
            embed.add_field(
                name="Up Next",
                value="No songs in queue",
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Music(bot))