# Langchain

## Getting Started

Let's get started by showing how to interact with the Azure OpenAI service using langchain packages and libraries. This will provide some insight into the configuration and setup that is needed to use one of these higher level abstraction frameworks.

[Langchain Notebook](langchain.ipynb)

## Langchain in an Application

The following section will demonstrate how to take the simple langchain interaction above and use it in an application. For the purposes of this exercise we will use fastapi along with uvicorn to host the Python web-based application.

1. Create a new folder for the application (apps/fastapi-langchain)
2. Copy the "main.py" and "requirements.txt" file from this folder to the newly created folder
3. Have a look at the "main.py file" to see the different endpoints available
4. Navigate to the newly created folder and type the following command to install the required packages:

```bash
pip install -r requirements.txt
```

5. Start the application using the following command:

```bash
uvicorn main:app --reload
```

6. Open a browser and navigate to http://localhost:8000/docs
7. Click on the "POST /completion" endpoint and then click on "Try it out"
