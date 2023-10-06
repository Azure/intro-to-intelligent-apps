using System.Text;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.SemanticFunctions;
using Microsoft.SemanticKernel.Orchestration;
using Microsoft.SemanticKernel.SkillDefinition;
using Azure;
using Azure.Search.Documents;
using Azure.Search.Documents.Models;
using Azure.AI.OpenAI;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;

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

// Add services to the container.
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Configure the HTTP request pipeline.
app.UseSwagger();
app.UseSwaggerUI();
app.UseHttpsRedirection();

// Configure Routing
app.MapPost("/completion", async ([FromServices] IKernel kernel, [FromBody] CompletionRequest request) =>
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

        // Create a prompt template with variables, note the double curly braces with dollar sign for the variables.
        // The PromptTemplate which was setup as inline SemanticFunction in the Polyglot notebook setup has been moved
        // into the Plugins directory so it is easier to manage and configure. Picture the ability to mount updated
        // prompt files into a container without having to rewrite the source code.
        var pluginsDirectory = Path.Combine(System.IO.Directory.GetCurrentDirectory(), "Plugins");
        var customPlugin = kernel.ImportSemanticSkillFromDirectory(pluginsDirectory, "CustomPlugin");

        Console.WriteLine("Semantic Function GetIntent with SK has been completed.");

        // Get Embedding for the original question
        OpenAIClient azureOpenAIClient = new OpenAIClient(new Uri(openai_api_base),new AzureKeyCredential(openai_api_key));
        float[] questionEmbedding = azureOpenAIClient.GetEmbeddings(embedding_name, new EmbeddingsOptions(request.Question)).Value.Data[0].Embedding.ToArray();

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
            ["original_question"] = request.Question,
            ["search_results"] = stringBuilderResults.ToString()
        };
        // Use SK Chaining to Invoke Semantic Function
        string completion = (await kernel.RunAsync(variables, customPlugin["GetIntent"])).Result;
        Console.WriteLine(completion);

        Console.WriteLine("Implementation of RAG using SK, C# and Azure Cognitive Search has been completed.");

        return new CompletionResponse(completion);
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

public record CompletionResponse (string Completion) {}