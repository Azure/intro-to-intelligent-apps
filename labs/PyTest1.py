import json
import requests
import os
from dotenv import load_dotenv

# Load environment variables
if load_dotenv():
    print("Found Azure OpenAI API Base Endpoint: " + os.getenv("AZURE_OPENAI_ENDPOINT"))
else: 
    print("Azure OpenAI API Base Endpoint not found. Have you configured the .env file?")
    
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = os.getenv("OPENAI_API_VERSION")
RESOURCE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

DEPLOYMENT_ID = os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME")

url = RESOURCE_ENDPOINT + "/openai/deployments/" + DEPLOYMENT_ID + "/chat/completions?api-version=" + API_VERSION

print(url)
