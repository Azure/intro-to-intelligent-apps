import os
from langchain.llms import AzureOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import Vector
from azure.search.documents import SearchClient

# Load environment variables
if load_dotenv():
    print("Found OpenAPI Base Endpoint: " + os.getenv("OPENAI_API_BASE"))
else: 
    print("No file .env found")

openai_api_type = os.getenv("OPENAI_API_TYPE")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_base = os.getenv("OPENAI_API_BASE")
openai_api_version = os.getenv("OPENAI_API_VERSION")
deployment_name = os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME")
embedding_name = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
acs_service_name = os.getenv("AZURE_COGNITIVE_SEARCH_SERVICE_NAME")
acs_endpoint_name = os.getenv("AZURE_COGNITIVE_SEARCH_ENDPOINT_NAME")
acs_index_name = os.getenv("AZURE_COGNITIVE_SEARCH_INDEX_NAME")
acs_api_key = os.getenv("AZURE_COGNITIVE_SEARCH_API_KEY")
print("openai_api_type = " + openai_api_type)
print("Configuration loaded.")

# Create an Embeddings Instance of Azure OpenAI
embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    deployment=embedding_name,
    openai_api_type = openai_api_type,
    openai_api_version = openai_api_version,
    openai_api_base = openai_api_base,
    openai_api_key = openai_api_key
)
# Create a Completion Instance of Azure OpenAI
llm = AzureChatOpenAI(
    model="gpt-3.5-turbo",
    deployment_name = deployment_name,
    openai_api_type = openai_api_type,
    openai_api_version = openai_api_version,
    openai_api_base = openai_api_base,
    openai_api_key = openai_api_key,
    temperature=0.1,
    max_tokens=500
)
print('Completed creation of embedding and completion instances.')

# Start the App
app = FastAPI()

class CompletionRequest(BaseModel):
    Question: str

class CompletionResponse(BaseModel):
    Completion: str

@app.get("/", response_class=HTMLResponse)
def read_root():
    return "<a href=docs>Swagger Endpoint: docs</a>"

@app.post("/completion/", response_class=JSONResponse)
def execute_completion(request: CompletionRequest):
    # Ask the question
    # The question is being passed in via the message body.
    # request: CompletionRequest
    
    # Create a prompt template with variables, note the curly braces
    prompt = PromptTemplate(
        input_variables=["original_question","search_results"],
        template="""
        Question: {original_question}

        Do not use any other data.
        Only use the movie data below when responding.
        {search_results}
        """,
    )

    # Get Embedding for the original question
    question_embedded=embeddings.embed_query(request.Question)

    # Search Vector Store
    search_client = SearchClient(
        acs_endpoint_name,
        acs_index_name,
        AzureKeyCredential(acs_api_key)
    )
    vector = Vector(
        value=question_embedded,
        k=5,
        fields="content_vector"
    )
    results = list(search_client.search(
        search_text="",
        include_total_count=True,
        vectors=[vector],
        select=["content"],
    ))

    # Build the Prompt and Execute against the Azure OpenAI to get the completion
    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
    response = chain.run({"original_question": request.Question, "search_results": results})
    print(response)
    return CompletionResponse(Completion = response)
