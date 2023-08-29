# 02 - Integrating AI into Applications

In this folder you will find exercises for integrating large language models (LLMs) into applications. We introduce the OpenAI API's, the OpenAI Libraries and the LangChain and Semantic Kernel *orchestrators*.

Below is a list of each of the labs in this section and what each one sets out to achieve.

## 00-PythonModules

[Python Modules](00-PythonModules/pythonmodules.ipynb)

Start with this lab initially. This will install some Python modules that are used in later labs.

## 01-AzureOpenAIAPI

[Azure OpenAI API](01-AzureOpenAIAPI/azureopenaiapi.ipynb)

In this lab, we'll walk through showing how to interact with an Azure OpenAI API service endpoint. This will not likely be the best option for most scenarios, but it highlights what a direct call to the underlying rest-based API looks like and will give you an appreciation of what's going on behind the scenes when you use the orchestrators in the other exercises.

## 02-OpenAIPackages

[OpenAI Packages/Libraries](02-OpenAIPackages/openai.ipynb)

In this lab we'll show how to interact with the Azure OpenAI API using the OpenAI Python library. This will provide some insight into the configuration and setup that is needed to use one of these higher level abstraction frameworks.

## 03-Langchain

[Langchain](03-Langchain/langchain.ipynb)

The third lab will demonstrate how to use Langchain with Azure OpenAI and how to set up a simple chain to perform basic AI orchestration.

## 04-SemanticKernel

[Semantic Kernel](04-SemanticKernel/semantickernel.ipynb)

The fourth lab is used to perform similar tasks to the third lab, but this time using Semantic Kernel instead of Langchain.
