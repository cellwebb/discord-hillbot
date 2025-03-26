import asyncio
from unittest.mock import patch

import pytest
import pytest_asyncio

from hillbot.image_generation import generate_image


class MockMessage:
    async def send(self, content, file=None):
        pass

    async def typing(self):
        return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    content = "!image test prompt"
    channel = None


@pytest_asyncio.fixture
async def mock_message():
    message = MockMessage()
    message.channel = message
    return message


@pytest.mark.asyncio
@patch("hillbot.image_generation.openai_client.images.generate")
async def test_generate_image(mock_generate, mock_message):
    # Call the function
    await generate_image(mock_message)

    # Assert that the mock was called
    mock_generate.assert_called_once()
