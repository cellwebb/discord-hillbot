from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from hillbot.image_generation import extract_prompt, generate_image


class MockMessage:
    def __init__(self):
        self.send = AsyncMock()
        self.typing = AsyncMock(return_value=None)
        self.channel = None
        self.content = "!image test prompt"

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


@pytest_asyncio.fixture
async def mock_message():
    message = MockMessage()
    message.channel = message
    return message


@pytest.mark.asyncio
@patch("hillbot.image_generation.create_image_from_prompt")
async def test_generate_image(mock_create, mock_message):
    # Setup the mock return value
    mock_create.return_value = (
        "test_filename.png",
        "enhanced prompt",
        "revised prompt",
    )

    # Call the function
    await generate_image(mock_message)

    # Assert that the mocks were called with correct arguments
    mock_create.assert_called_once_with("test prompt")
    assert mock_message.send.called


@pytest.mark.asyncio
async def test_extract_prompt():
    # Test with valid prefix
    result = await extract_prompt("!image test prompt")
    assert result == "test prompt"

    # Test with alternative prefix
    result = await extract_prompt("!img another test")
    assert result == "another test"

    # Test with no valid prefix
    result = await extract_prompt("hello world")
    assert result == ""
