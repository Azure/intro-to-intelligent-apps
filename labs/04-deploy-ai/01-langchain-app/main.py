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
openai_api_type = os.getenv("OPENAI_API_TYPE")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_base = os.getenv("OPENAI_API_BASE")
openai_api_version = os.getenv("OPENAI_API_VERSION")
deployment_name = os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME")
embedding_name = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")

# Create an instance of Azure OpenAI
llm = AzureOpenAI(
    openai_api_type = openai_api_type,
    openai_api_version = openai_api_version,
    openai_api_base = openai_api_base,
    openai_api_key = openai_api_key,
    deployment_name = deployment_name
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
