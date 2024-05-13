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

// Add Semantic Kernel service to the container.
// Add in configuration options and required services.
builder.Services.AddSingleton<ILogger>(sp => sp.GetRequiredService<ILogger<Program>>()); // some services require an un-templated ILogger

builder.Services.AddSingleton<IChatCompletionService>(sp =>
{
    return new AzureOpenAIChatCompletionService(azure_openai_completion_deployment_name, azure_openai_endpoint, azure_openai_api_key);
});

builder.Services.AddAzureOpenAIChatCompletion(azure_openai_completion_deployment_name, azure_openai_endpoint, azure_openai_api_key);
builder.Services.AddKernel();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Configure the HTTP request pipeline.
app.UseSwagger();
app.UseSwaggerUI();
app.UseHttpsRedirection();

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

// Start the Process
await app.RunAsync();

public record CompletionRequest (string Question) {}

public record CompletionResponse (string completion) {}