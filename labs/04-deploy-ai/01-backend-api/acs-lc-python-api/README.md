# 04 - Deploy ACS Langchain Python API

In this folder you will find a sample AI App that is built using Python, Langchain and Azure Cognitive Search.

The entire solution is in this folder, but we also have all the step by step instructions so you can see how it was built.

## Complete Solution

1. To test locally fill in `.env` with the same values from the .env file that was used for the Jupyter Notebooks.
2. Build and Run the App

```bash
uvicorn main:app --reload --host=0.0.0.0 --port=5291
```

## Step by Step Instructions

### Create Python Project and Solution

```bash
mkdir acs-lc-python
cd acs-lc-python
```

### Add Dependencies

```bash
echo "azure-core==1.29.3
azure-identity==1.14.0
azure-search-documents==11.4.0b8
fastapi==0.99.1
uvicorn==0.23.2
openai==0.27.9
langchain==0.0.312
tiktoken==0.4.0
python-dotenv==1.0.0" > requirements.txt
```

```bash
pip install -r requirements.txt
```

### Create main.py

```bash
echo "" > main.py
```

The first thing we need to do is to add some import and from statements to the `main.py` file.

```python
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
```

Next we read in the environment variables the same way we did in the notebook.

```python
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
```

Next we add the Embeddings and ChatCompletion instances of Azure OpenAI that we will be using.

```python
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
```

Next we start the app.

```python
# Start the App
app = FastAPI()
```

Next we define the class and routing methods that will be used.

```python
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
```

### Test the App

Now that we have all the code in place let's run it.

```bash
uvicorn main:app --reload --host=0.0.0.0 --port=5291
```

Once the app is started, open a browser and navigate to http://127.0.0.1:5291/docs
>**Note:** the port number may be different to `5291`, so double check the output from the `uvicorn main:app` command.

Click on the "POST /completion" endpoint, click on "Try it out", enter a Prompt, "List the movies about ships on the water.", then click on "Execute".

### Build and Test Docker Image

Let's now package the solution into a Docker Image so it can be deployed to a container service like Azure Kubernetes Serivce (AKS) or Azure Container Apps (ACA).

```bash
docker build -t acs-lc-python:v1 .
```

We can then test the image and be sure to set the environment variables so they override the values in the appsettings.json file. We don't want to have sensitive information embedded directly into the image.

```bash
docker run -it --rm \
    --name acslcpython \
    -p 5291:5291 \
    -e OPENAI_API_TYPE="Set this to "azure" for API key authentication or "azure_ad" for Azure AD authentication>", \
    -e OPENAI_API_KEY="<YOUR AZURE OPENAI API KEY - If using Azure AD auth, this can be left empty>" \
    -e OPENAI_API_BASE="<YOUR AZURE OPENAI ENDPOINT>" \
    -e OPENAI_API_VERSION="2023-05-15" \
    -e OPENAI_COMPLETION_MODEL="<YOUR OPENAI COMPLETIONS MODEL NAME - e.g. gpt-35-turbo>" \
    -e AZURE_TENANT_ID="<AZURE AD TENANT ID - Only used if you are using Azure AD to authentication>" \
    -e AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME="<YOUR AZURE OPENAI COMPLETIONS DEPLOYMENT NAME - e.g. gpt-35-turbo>" \
    -e AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME="<YOUR AZURE OPENAI EMBEDDINGS DEPLOYMENT NAME - e.g. text-embedding-ada-002>" \
    -e AZURE_COGNITIVE_SEARCH_SERVICE_NAME="<YOUR AZURE COGNITIVE SEARCH SERVICE NAME - e.g. cognitive-search-service>" \
    -e AZURE_COGNITIVE_SEARCH_ENDPOINT_NAME="<YOUR AZURE COGNITIVE SEARCH ENDPOINT NAME - e.g. https://cognitive-search-service.search.windows.net" \
    -e AZURE_COGNITIVE_SEARCH_INDEX_NAME="<YOUR AZURE COGNITIVE SEARCH INDEX NAME - e.g. cognitive-search-index>" \
    -e AZURE_COGNITIVE_SEARCH_API_KEY="<YOUR AZURE COGNITIVE SEARCH ADMIN API KEY - e.g. cognitive-search-admin-api-key>" \
    acs-lc-python:v1
```