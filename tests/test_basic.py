"""Basic tests for the Discord bot."""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

class TestBotBasic(unittest.IsolatedAsyncioTestCase):
    """Basic test cases for the Discord bot."""

    async def test_ai_response(self):
        """Test AI response generation."""
        from cogs.ai import AI
        
        # Mock the necessary parts
        bot = MagicMock()
        cog = AI(bot)
        
        # Test with a simple question
        response = await cog.get_ai_response("Hello, how are you?")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    @patch('discord.ext.commands.Bot')
    async def test_bot_initialization(self, mock_bot):
        """Test bot initialization."""
        import bot as bot_module
        
        # Test bot initialization
        await bot_module.on_ready()
        self.assertTrue(True)  # If we get here, initialization didn't crash

if __name__ == '__main__':
    unittest.main()
