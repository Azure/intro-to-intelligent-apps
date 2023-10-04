# 04 - Deploy AI App

In this folder you will find a sample AI App that is built using C#, Semantic Kernel and Azure Cognitive Search.

The entire solution is in this folder, but we also have all the step by step instructions so you can see how it was built.

## Complete Solution

1. To test locally fill in appsettings.json with the same values from the .env file that was used for the Jupyter Notebooks.
2. Build and Run the App

```csharp
dotnet run
```

## Step by Step Instructions

### Create C# Project and Solution

```csharp
mkdir acs-sk-csharp
cd acs-sk-csharp

dotnet new webapi --use-minimal-apis
dotnet new solution
dotnet sln acs-sk-csharp.sln add acs-sk-csharp.csproj
```

### Add Dependencies

```csharp
dotnet add acs-sk-csharp.csproj package Azure.Core --version "1.35.0"
dotnet add acs-sk-csharp.csproj package Azure.AI.OpenAI --version "1.0.0-beta.7"
dotnet add acs-sk-csharp.csproj package Microsoft.SemanticKernel --version "0.24.230918.1-preview"
dotnet add acs-sk-csharp.csproj package Microsoft.SemanticKernel.Abstractions --version "0.24.230918.1-preview"
dotnet add acs-sk-csharp.csproj package Azure.Search.Documents --version "11.5.0-beta.4"
```

### Update Program.cs

The first thing we need to do is to add some Using statements.

```csharp
using System.Text;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.SemanticFunctions;
using Microsoft.SemanticKernel.Orchestration;
using Microsoft.SemanticKernel.SkillDefinition;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Azure.AI.OpenAI;
```

Next we read in the variables. Because this is ASP.NET Core we will switch from the DotEnv package to native ASP.NET Core Configuration.

```csharp
var builder = WebApplication.CreateBuilder(args);

// Load values into variables
var config = builder.Configuration;
var openai_api_type = config["OPENAI_API_TYPE"] ?? String.Empty;
var openai_api_key = config["OPENAI_API_KEY"] ?? String.Empty;
var openai_api_base = config["OPENAI_API_BASE"] ?? String.Empty;
var openai_api_version = config["OPENAI_API_VERSION"] ?? String.Empty;
var deployment_name = config["AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME"] ?? String.Empty;
var embedding_name = config["AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"] ?? String.Empty;
var acs_service_name = config["AZURE_COGNITIVE_SEARCH_SERVICE_NAME"] ?? String.Empty;
var acs_endpoint_name = config["AZURE_COGNITIVE_SEARCH_ENDPOINT_NAME"] ?? String.Empty;
var acs_index_name = config["AZURE_COGNITIVE_SEARCH_INDEX_NAME"] ?? String.Empty;
var acs_api_key = config["AZURE_COGNITIVE_SEARCH_API_KEY"] ?? String.Empty;
Console.WriteLine($"openai_api_type = {openai_api_type}");
Console.WriteLine("Configuration loaded.");
```

Next we add the Semantic Kernel to the ASP.NET Core dependency injection container.

```csharp
// Add Semantic Kernel service to the container.
// Add in configuration options and required services.
builder.Services.AddSingleton<ILogger>(sp => sp.GetRequiredService<ILogger<Program>>()); // some services require an un-templated ILogger
builder.Services.AddScoped(sp =>
{
    // Setup Semantic Kernel
    IKernel kernel = Kernel.Builder
        .WithLoggerFactory(sp.GetRequiredService<ILoggerFactory>())
        .WithAzureChatCompletionService(deployment_name, openai_api_base, openai_api_key)
        .WithAzureTextEmbeddingGenerationService(embedding_name, openai_api_base, openai_api_key)
        .Build();
    
    Console.WriteLine("SK Kernel with ChatCompletion and EmbeddingsGeneration services created.");

    return kernel;
});
```

Next we swap out the app.MapGet weatherforecast function with our own.

```csharp
// Configure Routing
app.MapPost("/completion", async ([FromServices] IKernel kernel, [FromBody] string question) =>
{
    try
    {
        // Read values from .env file
        // These are loaded during startup, see above for details.

        // Setup Semantic Kernel
        // This has already been setup as part of the ASP.NET Core dependency injection setup
        // and is passed into this function as a parameter.
        // [FromServices] IKernel kernel

        // Ask the question
        // The question is being passed in via the message body.
        // [FromBody] string question

        // Create a prompt template with variables, note the double curly braces with dollar sign for the variables
        // First let's create the prompt string.
        var sk_prompt = @"
        Question: {{$original_question}}

        Do not use any other data.
        Only use the movie data below when responding.
        {{$search_results}}
        -e ;
        // Create the PromptTemplateConfig
        PromptTemplateConfig promptConfig = new PromptTemplateConfig
        {
            Schema = 1,
            Type = "completion",
            Description = "Gets the intent of the user.",
            Completion = 
            {
                Temperature = 0.1,
                TopP = 0.5,
                PresencePenalty = 0.0,
                FrequencyPenalty = 0.0,
                MaxTokens = 500
                // StopSequences = null,
                // ChatSystemPprompt = null;
            },
            Input = 
            {
                Parameters = new List<PromptTemplateConfig.InputParameter>
                {
                    new PromptTemplateConfig.InputParameter
                    {
                        Name="original_question",
                        Description="The user's request.",
                        DefaultValue=""
                    },
                    new PromptTemplateConfig.InputParameter
                    {
                        Name="search_results",
                        Description="Vector Search results from Azure Cognitive Search.",
                        DefaultValue=""
                    }
                }
            }
        };
        // Create the SemanticFunctionConfig object
        PromptTemplate promptTemplate = new PromptTemplate(
            sk_prompt,
            promptConfig,
            kernel
        );
        SemanticFunctionConfig functionConfig = new SemanticFunctionConfig(promptConfig, promptTemplate);
        // Register the GetIntent function with the Kernel
        ISKFunction getIntentFunction = kernel.RegisterSemanticFunction("CustomPlugin", "GetIntent", functionConfig);

        Console.WriteLine("Semantic Function GetIntent with SK has been completed.");

        // Get Embedding for the original question
        OpenAIClient azureOpenAIClient = new OpenAIClient(new Uri(openai_api_base),new AzureKeyCredential(openai_api_key));
        float[] questionEmbedding = azureOpenAIClient.GetEmbeddings(embedding_name, new EmbeddingsOptions(question)).Value.Data[0].Embedding.ToArray();

        Console.WriteLine("Embedding of original question has been completed.");

        // Search Vector Store
        SearchOptions searchOptions = new SearchOptions
        {
            // Filter to only Content greater than or equal our preference
            // Filter = SearchFilter.Create($"Content ge {content}"),
            // OrderBy = { "Content desc" } // Sort by Content from high to low
            // Size = 5, // Take only 5 results
            // Select = { "id", "content", "content_vector" }, // Which fields to return
            Vectors = { new() { Value = questionEmbedding, KNearestNeighborsCount = 5, Fields = { "content_vector" } } }, // Vector Search
            Size = 5,
            Select = { "id", "content" },
        };

        // Note the search text is null and the vector search is filled in.
        AzureKeyCredential credential = new AzureKeyCredential(acs_api_key);
        SearchClient searchClient = new SearchClient(new Uri(acs_endpoint_name), acs_index_name, credential);
        SearchResults<SearchDocument> response = searchClient.Search<SearchDocument>(null, searchOptions);
        Pageable<SearchResult<SearchDocument>> results = response.GetResults();
        // Create string from the results
        StringBuilder stringBuilderResults = new StringBuilder();
        foreach (SearchResult<SearchDocument> result in results)
        {
            stringBuilderResults.AppendLine($"{result.Document["content"]}");
        };

        Console.WriteLine("Searching of Vector Store has been completed.");

        // Build the Prompt and Execute against the Azure OpenAI to get the completion
        // Initialize the prompt variables
        ContextVariables variables = new ContextVariables
        {
            ["original_question"] = question,
            ["search_results"] = stringBuilderResults.ToString()
        };
        // Use SK Chaining to Invoke Semantic Function
        string completion = (await kernel.RunAsync(variables, getIntentFunction)).Result;
        Console.WriteLine(completion);

        Console.WriteLine("Implementation of RAG using SK, C# and Azure Cognitive Search has been completed.");

        return completion;
    }
    catch (Exception exc)
    {
        Console.WriteLine($"Error: {exc.Message}");
        return "Something unexpected happened.";
    }
})
.WithName("Completion")
.WithOpenApi();
```

Last, but not least we change the app.Run() to be async.

```csharp
await app.RunAsync();
```

### Test the App

Now that we have all the code in place let'c compile and run it.

```csharp
dotnet run
```

Once the app is started, open a browser and navigate to http://127.0.0.1:5291/swagger/index.html 

Click on the "POST /completion" endpoint, click on "Try it out", enter a Prompt, "List the movies about ships on the water.", then click on "Execute".

### Build and Test Docker Image

Let's now package the solution into a Docker Image so it can be deployed to a container service like Azure Kubernetes Serivce (AKS) or Azure Container Apps (ACA).

```bash
docker build -t acs-sk-csharp:v1 .
```

We can then test the image and be sure to set the environment variables so they override the values in the appsettings.json file. We don't want to have sensitive information embedded directly into the image.

```bash
docker run -it --rm \
    --name acsskcsharp \
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
    acs-sk-csharp:v1
```