"""
Template for pytest test files

This file demonstrates the structure and best practices for writing tests in the project.
"""

from unittest.mock import AsyncMock, patch

import pytest

# Example: Testing a simple utility function
from hillbot.utils.utils import format_message


@pytest.mark.unit
class TestFormatMessage:
    """Test format_message function"""

    @pytest.fixture
    def mock_discord_message(self):
        """Mock Discord message"""
        mock = AsyncMock()
        mock.content = "test message"
        mock.author.name = "Test User"
        return mock

    @pytest.mark.asyncio
    async def test_format_message_success(self, mock_discord_message):
        """Test successful message formatting"""
        # Arrange
        expected_result = "[Test User]: test message"

        # Act
        result = await format_message(mock_discord_message)

        # Assert
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_format_message_empty(self, mock_discord_message):
        """Test empty message formatting"""
        # Arrange
        mock_discord_message.content = ""
        expected_result = "[Test User]: "

        # Act
        result = await format_message(mock_discord_message)

        # Assert
        assert result == expected_result


if __name__ == "__main__":
    pytest.main(["-v", "--cov", "--cov-report=term-missing"])
