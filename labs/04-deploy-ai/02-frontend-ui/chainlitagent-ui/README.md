# Building an app with Chainlit

The following section will demonstrate how to build a sample AI App using Chainlit. Chainlit is a tool that allows you to build AI applications with ease, by providing a simple interface to interact with AI models.

The official docs can be found here: https://docs.chainlit.io.

The app in this folder will connect to one of the backend applications in the `01-backend-api` folder. You can use either the Python/Langchain or .NET/Semantic Kernel version, either will work.

Start one of the backend applications first, test and ensure the backend is working before starting the frontend.

To run the chainlit application, follow the steps below:

1. Install any requirements

```bash
pip install -r requirements.txt
```

2. Start the application using the following command:

```bash
chainlit run app.py -w
```

3. After a few moments, a browser window should open automatically. If not, go to a browser and navigate to http://localhost:8000/
4. Enter a prompt in the box at the bottom of the screen and hit "Enter". Remember that the backend has been configured to answer questions about the movies that we uploaded to Azure AI Search.