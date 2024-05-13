# 04 - Deploy ACS Langchain Python API

In this folder you will find a sample AI App that is built using Python, Langchain and Azure AI Search.

The entire solution is in this folder, but we also have all the step by step instructions so you can see how it was built.

## Complete Solution

To test the version of the app in this folder, you should just be able to run the command below. It should read the environment variable values from the `.env` file located in the root of this repository, so if you've already configured that there shouldn't be anything else to do. Otherwise, you'll need to fill in the `.env` file with the necessary values.

You can run the app using the command below.

```bash
uvicorn main:app --reload --host=0.0.0.0 --port=5291
```

## Step by Step Instructions

### Create Python Project and Solution

```bash
mkdir aais-lc-python
cd aais-lc-python
```

### Add Dependencies

```bash
echo "azure-core==1.30.1
azure-identity==1.16.0
azure-search-documents==11.4.0
fastapi==0.110.1
uvicorn==0.25.0
openai==1.27.0
langchain==0.1.19
langchain-openai==0.1.3
tiktoken==0.6.0
python-dotenv==1.0.1
chainlit==1.0.506" > requirements.txt
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
```

We configure some logging so we can see what's happening behind the scenes

```python
logging.basicConfig(format='%(levelname)-10s%(message)s', level=logging.INFO)
```

Next we read in the environment variables.

```python
if load_dotenv():
    logging.info("Azure OpenAI Endpoint: " + os.getenv("AZURE_OPENAI_ENDPOINT"))
    logging.info("Azure AI Search: " + os.getenv("AZURE_AI_SEARCH_SERVICE_NAME"))
else: 
    print("No file .env found")
```

Now we add the Embeddings and ChatCompletion instances of Azure OpenAI that we will be using.

```python
# Create an Embeddings Instance of Azure OpenAI
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
    completion: str
```

This route is for the root of the app, it will return a link to the Swagger UI.

```python
@app.get("/", response_class=HTMLResponse)
def read_root():
    return "<a href=docs>Swagger Endpoint: docs</a>"
```

This route is for the completion endpoint, it will take a question and return a completion. The question is first passed to Azure AI Search to get the top 5 results, then the question and results are passed to Azure OpenAI to get a completion.

```python
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
        os.getenv("AZURE_AI_SEARCH_ENDPOINT"),
        os.getenv("AZURE_AI_SEARCH_INDEX_NAME"),
        AzureKeyCredential(os.getenv("AZURE_AI_SEARCH_API_KEY"))
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
```

### Test the App

Now that we have all the code in place let's run it.

Remember to create a `.env` file in the same folder as the `main.py` file and add the environment variables and values we used from the `.env` file in the Jupyter notebooks.

```bash
uvicorn main:app --reload --host=0.0.0.0 --port=5291
```

Once the app is started, open a browser and navigate to http://127.0.0.1:5291/docs
>**Note:** the port number may be different to `5291`, so double check the output from the `uvicorn main:app` command.

Click on the "POST /completion" endpoint, click on "Try it out", enter a Prompt, "List the movies about ships on the water.", then click on "Execute".

### Build and Test Docker Image

Let's now package the solution into a Docker Image so it can be deployed to a container service like Azure Kubernetes Serivce (AKS) or Azure Container Apps (ACA).

First you'll need to create a Dockerfile

```bash
echo "" > Dockerfile
```

Next, paste the following into the Dockerfile

```Dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y \
  build-essential \
  curl \
  software-properties-common \
  git \
  && rm -rf /var/lib/apt/lists/*
# Create a virtualenv to keep dependencies together
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2 - Copy only necessary files to the runner stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY main.py .
EXPOSE 5291
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=5291"]
```

Next, we build the Docker Image.

```bash
docker build -t aais-lc-python:v1 .
```

Finally, we can test the image. We pass in the environment variable values as we don't want to have sensitive information embedded directly into the image.

```bash
docker run -it --rm \
    --name aaislcpython \
    -p 5291:5291 \
    -e AZURE_OPENAI_API_KEY="<YOUR AZURE OPENAI API KEY>" \
    -e AZURE_OPENAI_ENDPOINT="<YOUR AZURE OPENAI ENDPOINT>" \
    -e OPENAI_API_VERSION="2024-03-01-preview" \
    -e AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME="<YOUR AZURE OPENAI COMPLETIONS DEPLOYMENT NAME - e.g. gpt-35-turbo>" \
    -e AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME="<YOUR AZURE OPENAI EMBEDDINGS DEPLOYMENT NAME - e.g. text-embedding-ada-002>" \
    -e AZURE_OPENAI_EMBEDDING_MODEL="<YOUR AZURE OPENAI EMBEDDINGS MODEL NAME - e.g. text-embedding-ada-002>" \
    -e AZURE_AI_SEARCH_SERVICE_NAME="<YOUR AZURE AI SEARCH SERVICE NAME - e.g. cognitive-search-service>" \
    -e AZURE_AI_SEARCH_ENDPOINT="<YOUR AZURE AI SEARCH ENDPOINT NAME - e.g. https://cognitive-search-service.search.windows.net" \
    -e AZURE_AI_SEARCH_INDEX_NAME="<YOUR AZURE AI SEARCH INDEX NAME - e.g. cognitive-search-index>" \
    -e AZURE_AI_SEARCH_API_KEY="<YOUR AZURE AI SEARCH ADMIN API KEY - e.g. cognitive-search-admin-api-key>" \
    aais-lc-python:v1
```