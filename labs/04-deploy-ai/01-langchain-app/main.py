import os
# Import Azure OpenAI
from langchain.llms import AzureOpenAI
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

# Load environment variables
if load_dotenv():
    print("Found OpenAPI Base Endpoint: " + os.getenv("OPENAI_API_BASE"))
else: 
    print("No file .env found")

# Configure OpenAI API
openai_api_type = os.getenv("OPENAI_TYPE")
openai_api_version = os.getenv("OPENAI_VERSION")
openai_api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
COMPLETION_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Create an instance of Azure OpenAI
llm = AzureOpenAI(
    openai_api_type = openai_api_type,
    openai_api_version = openai_api_version,
    openai_api_base = openai_api_base,
    openai_api_key = openai_api_key,
    deployment_name = COMPLETION_DEPLOYMENT
)

# Start the App
app = FastAPI()

class Prompt(BaseModel):
    prompt: str
    max_tokens: int

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/completion/")
async def execute_completion(prompt: Prompt):
    response = llm(prompt.prompt)
    return {"response": response}
