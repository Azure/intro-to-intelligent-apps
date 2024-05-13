import os
import logging
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse, HTMLResponse
from langchain.prompts import PromptTemplate
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser

logging.basicConfig(format='%(levelname)-10s%(message)s', level=logging.INFO)

# Load environment variables
if load_dotenv():
    logging.info("Azure OpenAI Endpoint: " + os.getenv("AZURE_OPENAI_ENDPOINT"))
    logging.info("Azure AI Search: " + os.getenv("AZURE_AI_SEARCH_SERVICE_NAME"))
else: 
    print("No file .env found")

azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
openai_api_version = os.getenv("OPENAI_API_VERSION")
azure_openai_completion_deployment_name = os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME")
azure_openai_embedding_deployment_name = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
azure_ai_search_name = os.getenv("AZURE_AI_SEARCH_SERVICE_NAME")
azure_ai_search_endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
azure_ai_search_index_name = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")
azure_ai_search_api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")

azure_openai_embeddings = AzureOpenAIEmbeddings(
    azure_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
    openai_api_version = os.getenv("OPENAI_EMBEDDING_API_VERSION"),
    model= os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")
)

azure_openai = AzureChatOpenAI(
    azure_deployment = os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME"),
    temperature=0.1,
    max_tokens=500
)
logging.info('Completed creation of embedding and completion instances.')

# Start the App
app = FastAPI()

class CompletionRequest(BaseModel):
    Question: str

class CompletionResponse(BaseModel):
    completion: str

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

    # Search Vector Store
    search_client = SearchClient(
        azure_ai_search_endpoint,
        azure_ai_search_index_name,
        AzureKeyCredential(azure_ai_search_api_key)
    )

    vector = VectorizedQuery(vector=azure_openai_embeddings.embed_query(request.Question), k_nearest_neighbors=5, fields="vector")

    results = list(search_client.search(
        search_text=request.Question,
        query_type="semantic",
        semantic_configuration_name="movies-semantic-config",
        include_total_count=True,
        vector_queries=[vector],
        select=["title","genre","overview","tagline","release_date","popularity","vote_average","vote_count","runtime","revenue","original_language"],
        top=5
    ))

    output_parser = StrOutputParser()
    chain = prompt | azure_openai | output_parser
    response = chain.invoke({"original_question": request.Question, "search_results": results})
    logging.info("Response from LLM: " + response)
    return CompletionResponse(completion = response)
