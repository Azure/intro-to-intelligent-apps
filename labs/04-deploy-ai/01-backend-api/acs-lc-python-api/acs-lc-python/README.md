# Langchain in an Application

The following section will demonstrate how to take a simple langchain interaction like the one we created during the earlier labs and use it in an application. For the purposes of this exercise we will use fastapi along with uvicorn to host the Python web-based application.

Here are the steps at a high-level.

1. Install any requirements

```bash
pip install -r requirements.txt
```

2. Start the application using the following command:

```bash
uvicorn main:app --reload --host=0.0.0.0 --port=5291
```

3. Open a browser and navigate to http://localhost:8000/docs
4. Click on the "POST /completion" endpoint, click on "Try it out", enter a Prompt, then click on "Execute".