import os
import chainlit as cl
from dotenv import load_dotenv
import urllib.parse
import asyncio
import aiohttp
import json

# Load environment variables
if load_dotenv():
    print("Found OpenAPI Base Endpoint: " + os.getenv("BACKEND_API_BASE"))
else: 
    print("No file .env found")

backend_api_base = os.getenv("BACKEND_API_BASE")

@cl.on_chat_start
def main():
    # Add any objects or information needed for the user session.
    welcome = "Hello!"

    # Store objects or information user session
    cl.user_session.set("welcome", welcome)


@cl.on_message
async def main(message: str):
    # Retrieve any objects or information from the user session
    welcome = cl.user_session.get("welcome")  # type: welcome

    # Call the backend api httprequest asynchronously
    # encoded_data = urllib.parse.urlencode(message).encode("utf-8")
    headers = {'accept': 'application/json', 'content-type': 'application/json'}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(
            url=backend_api_base + "/completion",
            data='{ "question": "' + message + '"}'
        ) as response:
            res = await response.text()
    json_response = json.loads(res)
    print(json_response["completion"])

    # Do any post processing here

    # Send the response
    await cl.Message(content=json_response["completion"]).send()