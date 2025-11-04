"""
Helper utility functions for the Discord bot.
"""

import json
from pathlib import Path
from datetime import datetime
import os


def load_json(filename):
    """Load data from a JSON file."""
    filepath = Path('data') / filename
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_json(filename, data):
    """Save data to a JSON file."""
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    filepath = data_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def format_time(seconds):
    """Format seconds into a readable time string."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def parse_duration(duration_str):
    """
    Parse a duration string (e.g., '1h 30m', '5m', '30s') into seconds.
    Returns None if parsing fails.
    """
    duration_str = duration_str.lower().strip()
    total_seconds = 0
    
    try:
        # Try direct integer (seconds)
        if duration_str.isdigit():
            return int(duration_str)
        
        # Parse with units
        import re
        pattern = r'(\d+)\s*(h|m|s|hour|hours|min|mins|minute|minutes|sec|secs|second|seconds)'
        matches = re.findall(pattern, duration_str)
        
        if not matches:
            return None
        
        for value, unit in matches:
            value = int(value)
            if unit in ['h', 'hour', 'hours']:
                total_seconds += value * 3600
            elif unit in ['m', 'min', 'mins', 'minute', 'minutes']:
                total_seconds += value * 60
            elif unit in ['s', 'sec', 'secs', 'second', 'seconds']:
                total_seconds += value
        
        return total_seconds if total_seconds > 0 else None
    except:
        return None


def create_embed(title, description="", color=None, footer=None):
    """Create a Discord embed with common styling."""
    import discord
    if color is None:
        color = discord.Color.blue()
    
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    
    if footer:
        embed.set_footer(text=footer)
    
    return embed

