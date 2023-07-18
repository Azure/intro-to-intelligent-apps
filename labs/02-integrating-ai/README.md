# 02 - Integrating AI into Applications

In this folder you will find exercises for integrating large language models (LLMs) into applications. We introduce the OpenAI API's, the OpenAI Libraries and the LangChain and Semantic Kernel *orchestrators*.

For each exercise you will see how to setup a sample project and turn a prompt into a callable API endpoint.

The list below outlines some of the options for interacting and wrapping the Azure Open AI service. The first item in the list outlines how to interact with the raw Azure OpenAI API endpoint. This is not likely the best option for most scenarios, but it highlights what the underlying rest-based API looks like. The second item in the list is how to use the OpenAI packages and configure them for Azure OpenAI. The third item in the list is how to use the Semantic Kernel framework to wrap the Azure OpenAI API. The fourth item in the list is how to use Langchain to wrap the Azure OpenAI API.

The first two in the list are focused on the API structure and how to interact with the Azure OpenAI endpoints. The last two in the list are focused on how to orchestrate and chain multiple steps together which will then determine the appropriate way to interact with the Azure OpenAI API in a way that makes it easier to use in an application.

* [1) Azure OpenAI API](01-AzureOpenAIAPI/azureopenaiapi.md)
* [2) OpenAI Packages/Libraries](02-OpenAIPackages/openai.md)
* [3) Langchain](03-Langchain/langchain.md)
* [4) Semantic Kernel](04-SemanticKernel/semantickernel.ipynb)
