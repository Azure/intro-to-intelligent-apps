# 04 - Deploy AI

In this folder you will find exercises to help increase your understanding of how to deploy AI Apps to Azure.

Below is a list of each of the labs in this section and what each one sets out to achieve.

## 01-Backend API

Pick one of the following APIs to deploy depending on whether you are more oriented towards C# or Python development.

[ACS + Semantic Kernel C#](01-backend-api/acs-sk-csharp-api/README.md)

In this lab, we'll turn the 03-orchestration/04-ACS/acs-sk-csharp.ipynb notebook lab into an ASP.NET Core API that can then be consumed by the frontend UI application.

[ACS + Langchain Python](01-backend-api/acs-lc-python-api/README.md)

In this lab, we'll turn the 03-orchestration/04-ACS/acs-lc-python.ipynb notebook lab into a Python FastAPI API that can then be consumed by the frontend UI application.

## 02-Frontend UI

[Chat UI using Chainlit](02-frontend-ui/chainlitagent-ui/README.md)

In this lab, we'll walk through deploying a simple UI that will consume the ASP.NET Core or Python FastAPI API in the first deployment section above. The UI will be built using a ChainLit App built in Python which is a simple and easy way to quickly mockup a UI for a ChatGPT like experience.