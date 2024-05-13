# 04 - Deploy Azure AI Search Semantic Kernel C# API

In this folder you will find a sample AI App that is built using C#, Semantic Kernel and Azure AI Search.

The entire solution is in this folder, but we also have all the step by step instructions so you can see how it was built.

## Complete Solution

1. To test locally fill in `appsettings.json` with the same values from the .env file that was used earlier for the Jupyter Notebook based labs.
2. Build and Run the App

```bash
dotnet run
```

## Step by Step Instructions

### Create C# Project and Solution

```bash
mkdir aais-sk-csharp
cd aais-sk-csharp

dotnet new webapi --use-minimal-apis
dotnet new solution
dotnet sln aais-sk-csharp.sln add aais-sk-csharp.csproj
```

### Add Dependencies

```bash
dotnet add aais-sk-csharp.csproj package Azure.Core --version "1.39.0"
dotnet add aais-sk-csharp.csproj package Azure.AI.OpenAI --version "1.0.0-beta.16"
dotnet add aais-sk-csharp.csproj package Microsoft.SemanticKernel --version "1.10.0"
dotnet add aais-sk-csharp.csproj package Microsoft.SemanticKernel.Connectors.OpenAI --version "1.10.0"
dotnet add aais-sk-csharp.csproj package Azure.Search.Documents --version "11.5.0-beta.5"
```

### Update Program.cs

The first thing we need to do is to add some Using statements to the `Program.cs` file. Add the following right at the top of this file.

```csharp
using System.Text;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Connectors.OpenAI;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Azure.Search.Documents.Indexes;
using Azure.AI.OpenAI;
using Microsoft.AspNetCore.Mvc;
using Microsoft.SemanticKernel.ChatCompletion;
```

Next we read in the variables. Because this is ASP.NET Core we will switch from the DotEnv package we used in earlier labs to native ASP.NET Core Configuration.

```csharp
var builder = WebApplication.CreateBuilder(args);

// Load values into variables
var config = builder.Configuration;
var azure_openai_api_key = config["AZURE_OPENAI_API_KEY"] ?? String.Empty;
var azure_openai_endpoint = config["AZURE_OPENAI_ENDPOINT"] ?? String.Empty;
var openai_api_version = config["OPENAI_API_VERSION"] ?? String.Empty;
var azure_openai_completion_deployment_name = config["AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME"] ?? String.Empty;
var azure_openai_embedding_deployment_name = config["AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"] ?? String.Empty;
var azure_ai_search_name = config["AZURE_AI_SEARCH_SERVICE_NAME"] ?? String.Empty;
var azure_ai_search_endpoint = config["AZURE_AI_SEARCH_ENDPOINT"] ?? String.Empty;
var azure_ai_search_index_name = config["AZURE_AI_SEARCH_INDEX_NAME"] ?? String.Empty;
var azure_ai_search_api_key = config["AZURE_AI_SEARCH_API_KEY"] ?? String.Empty;
Console.WriteLine("Configuration loaded.");
```

Next we add the Semantic Kernel to the ASP.NET Core dependency injection container. Insert these lines after the configuration code above.

```csharp
// Add Semantic Kernel service to the container.
// Add in configuration options and required services.
builder.Services.AddSingleton<ILogger>(sp => sp.GetRequiredService<ILogger<Program>>()); // some services require an un-templated ILogger

builder.Services.AddSingleton<IChatCompletionService>(sp =>
{
    return new AzureOpenAIChatCompletionService(azure_openai_completion_deployment_name, azure_openai_endpoint, azure_openai_api_key);
});

builder.Services.AddAzureOpenAIChatCompletion(azure_openai_completion_deployment_name, azure_openai_endpoint, azure_openai_api_key);
builder.Services.AddKernel();
```

You can remove the section of code that defines `var summaries` as we don't need it for this sample.

Next we swap out the `app.MapGet` `weatherforecast` function with our own.

```csharp
// Configure Routing
app.MapPost("/completion", async ([FromServices] Kernel kernel, [FromBody] CompletionRequest request) =>
{
    try
    {
        // Read values from .env file
        // These are loaded during startup, see above for details.

        // Setup Semantic Kernel
        // This has already been setup as part of the ASP.NET Core dependency injection setup
        // and is passed into this function as a parameter.
        // [FromServices] Kernel kernel

        // Ask the question
        // The question is being passed in via the message body.
        // [FromBody] CompletionRequest request

        // The PromptTemplate which was setup as an inline function in the earlier labs has been moved
        // into the Plugins directory so it is easier to manage and configure. This gives the ability to mount updated
        // prompt files into a container without having to rewrite the source code.
        var pluginsDirectory = Path.Combine(System.IO.Directory.GetCurrentDirectory(), "Plugins");
        var customPlugin = kernel.ImportPluginFromPromptDirectory(Path.Combine(pluginsDirectory, "CustomPlugin"));
        Console.WriteLine("Plugin GetMovieInfo loaded.");

        // Get Embedding for the original question
        OpenAIClient azureOpenAIClient = new OpenAIClient(new Uri(azure_openai_endpoint),new AzureKeyCredential(azure_openai_api_key));
        float[] queryEmbedding = azureOpenAIClient.GetEmbeddings(new EmbeddingsOptions(azure_openai_embedding_deployment_name, new List<string>() { request.Question })).Value.Data[0].Embedding.ToArray();

        Console.WriteLine("Embedding of original question has been completed.");

        // Search Vector Store

        string semanticSearchConfigName = "movies-semantic-config";

        SearchOptions searchOptions = new SearchOptions
        {
            QueryType = SearchQueryType.Semantic,
            SemanticConfigurationName = semanticSearchConfigName,
            VectorQueries = { new RawVectorQuery() { Vector = queryEmbedding, KNearestNeighborsCount = 5, Fields = { "vector" } } },
            Size = 5,
            Select = { "title", "genre" },
        };

        AzureKeyCredential indexCredential = new AzureKeyCredential(azure_ai_search_api_key);
        SearchIndexClient indexClient = new SearchIndexClient(new Uri(azure_ai_search_endpoint), indexCredential);
        SearchClient searchClient = indexClient.GetSearchClient(azure_ai_search_index_name);

        //Perform the search
        SearchResults<SearchDocument> response = searchClient.Search<SearchDocument>(request.Question, searchOptions);
        Pageable<SearchResult<SearchDocument>> results = response.GetResults();

        // Create string from the results

        StringBuilder stringBuilderResults = new StringBuilder();
        foreach (SearchResult<SearchDocument> result in results)
        {
            stringBuilderResults.AppendLine($"{result.Document["title"]}");
        };

        Console.WriteLine(stringBuilderResults.ToString());

        Console.WriteLine("Searching of Vector Store has been completed.");

        // Build the Prompt and Execute against the Azure OpenAI to get the completion

        var completion = await kernel.InvokeAsync(customPlugin["GetMovieInfo"], new () { { "original_question", request.Question }, { "search_results", stringBuilderResults.ToString() }}); 
        Console.WriteLine("Implementation of RAG using SK, C# and Azure Cognitive Search has been completed.");
        Console.WriteLine(completion.ToString());
        return new CompletionResponse(completion.ToString());
    }
    catch (Exception exc)
    {
        Console.WriteLine($"Error: {exc.Message}");
        return new CompletionResponse("Something unexpected happened.");
    }
})
.WithName("Completion")
.WithOpenApi();
```

We'll replace the `app.Run()` with the async version.

```csharp
// Start the Process
await app.RunAsync();
```

We don't need the `WeatherForecast` record so we can remove that from the `Program.cs` file. We'll replace it with the following two records that are used for the question and completion.

```csharp
public record CompletionRequest (string Question) {}

public record CompletionResponse (string completion) {}
```

### Create a Plug In

With Semantic Kernel, we can define a prompt within a file and then use that file as a plug in. This allows us to define the prompt in a file and then mount that file into a container without having to change the source code.

In the root of the project create a folder called `Plugins` and in that folder create another folder called `CustomPlugin`.

```bash
mkdir Plugins
cd Plugins
mkdir CustomPlugin
```

The Plug In that we're going to create will be called `GetMovieInfo`, so let's create a folder for that too.

```bash
cd CustomPlugin
mkdir GetMovieInfo
```

Under the `GetMovieInfo` folder we will create two files. One file will provide the template for the prompt that we want to use with Azure OpenAI. The other file will provide the configuration parameters.

Create a file called `skprompt.txt` and add the following text.

```text
Question: {{$original_question}}

Do not use any other data.
Only use the movie data below when responding.
{{$search_results}}
```

Next, create a file named `config.json` and add the following.

```json
{
    "schema": 1,
    "type": "completion",
    "description": "Answers questions about provided movie data.",
    "completion": {
         "max_tokens": 500,
         "temperature": 0.1,
         "top_p": 0.5,
         "presence_penalty": 0.0,
         "frequency_penalty": 0.0
    },
    "input": {
         "parameters": [
            {
                "name": "original_question",
                "description": "The user's request.",
                "defaultValue": ""
            },
            {
                "name": "search_results",
                "description": "Vector Search results from Azure AI Search.",
                "defaultValue": ""
            }
         ]
    }
}
```

When you've completed the above steps, your folder structure should look like this.

```text
aais-sk-csharp
├── Plugins
│   ├── CustomPlugin
│   │   ├── GetMovieInfo
│   │   │   ├── config.json
│   │   │   ├── skprompt.txt
```

### Test the App

You'll first need to update the `appsettings.json` file to provide the values needed. After `AllowedHosts` add the following and replace the values with your own.

```json
  "OPENAI_API_VERSION": "2024-03-01-preview",
  "AZURE_OPENAI_API_KEY": "<YOUR AZURE OPENAI API KEY>",
  "AZURE_OPENAI_ENDPOINT": "<YOUR AZURE OPENAI ENDPOINT>",
  "AZURE_OPENAI_COMPLETION_MODEL": "<YOUR AZURE OPENAI COMPLETIONS MODEL NAME - e.g. gpt-35-turbo>",
  "AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME": "<YOUR AZURE OPENAI COMPLETIONS DEPLOYMENT NAME - e.g. gpt-35-turbo>",
  "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME": "<YOUR AZURE OPENAI EMBEDDINGS DEPLOYMENT NAME - e.g. text-embedding-ada-002>",
  "AZURE_AI_SEARCH_SERVICE_NAME": "<YOUR AZURE AI SEARCH SERVICE NAME - e.g. ai-vectorstore-abcd>",
  "AZURE_AI_SEARCH_ENDPOINT": "<YOUR AZURE AI SEARCH ENDPOINT - e.g. https://ai-vectorstore-abcd.search.windows.net>",
  "AZURE_AI_SEARCH_INDEX_NAME": "<YOUR AZURE AI SEARCH INDEX NAME - e.g. ai-search-index>",
  "AZURE_AI_SEARCH_API_KEY": "<YOUR AZURE AI SEARCH ADMIN API KEY>"
  ```

We'll also need to update the `aais-sk-csharp.csproj` file to include the `Plugins` directory in the build. By default, the `dotnet build` command will ignore `.txt` files, and we need the `skprompt.txt` file to be included in the build.

```xml
  <ItemGroup>
    <None Update="Plugins\**\*.txt">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </None>
  </ItemGroup>
```

Next we can compile and run the app.

```csharp
dotnet run
```

Once the app is started, open a browser and navigate to http://127.0.0.1:5291/swagger/index.html
>**Note:** the port number may be different to `5291`, so double check the output from the `dotnet run` command.

Click on the "POST /completion" endpoint, click on "Try it out", enter a Prompt, "List the movies about ships on the water.", then click on "Execute".

### Build and Test Docker Image

Let's now package the solution into a Docker Image so it can be deployed to a container service like Azure Kubernetes Serivce (AKS) or Azure Container Apps (ACA).

In the root of the project create a file called `Dockerfile` and add the following.

```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 5291
ENV ASPNETCORE_URLS=http://+:5291

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
ARG configuration=Release
WORKDIR /src
COPY ["aais-sk-csharp.csproj", "."]
RUN dotnet restore "aais-sk-csharp.csproj"
COPY ["Program.cs", "."]
COPY ["Plugins/", "./Plugins/"]
RUN dotnet build "aais-sk-csharp.csproj" -c $configuration -o /app/build

FROM build AS publish
ARG configuration=Release
RUN dotnet publish "aais-sk-csharp.csproj" -c $configuration -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "aais-sk-csharp.dll"]
```

Now run the following command to build the Docker image.

```bash
docker build -t aais-sk-csharp:v1 .
```

We can then test the image and be sure to set the environment variables so they override the values in the appsettings.json file. We don't want to have sensitive information embedded directly into the image.

```bash
docker run -it --rm \
    --name aaisskcsharp \
    -p 5291:5291 \
    -e AZURE_OPENAI_API_KEY="<YOUR AZURE OPENAI API KEY - If using Azure AD auth, this can be left empty>" \
    -e AZURE_OPENAI_ENDPOINT="<YOUR AZURE OPENAI ENDPOINT>" \
    -e OPENAI_API_VERSION="2024-03-01-preview" \
    -e AZURE_OPENAI_COMPLETION_MODEL="<YOUR OPENAI COMPLETIONS MODEL NAME - e.g. gpt-35-turbo>" \
    -e AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME="<YOUR AZURE OPENAI COMPLETIONS DEPLOYMENT NAME - e.g. gpt-35-turbo>" \
    -e AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME="<YOUR AZURE OPENAI EMBEDDINGS DEPLOYMENT NAME - e.g. text-embedding-ada-002>" \
    -e AZURE_AI_SEARCH_SERVICE_NAME="<YOUR AZURE COGNITIVE SEARCH SERVICE NAME - e.g. cognitive-search-service>" \
    -e AZURE_AI_SEARCH_ENDPOINT="<YOUR AZURE COGNITIVE SEARCH ENDPOINT NAME - e.g. https://cognitive-search-service.search.windows.net" \
    -e AZURE_AI_SEARCH_INDEX_NAME="<YOUR AZURE COGNITIVE SEARCH INDEX NAME - e.g. cognitive-search-index>" \
    -e AZURE_AI_SEARCH_API_KEY="<YOUR AZURE COGNITIVE SEARCH ADMIN API KEY - e.g. cognitive-search-admin-api-key>" \
    aais-sk-csharp:v1
```