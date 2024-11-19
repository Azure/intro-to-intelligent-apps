param name string
param location string = resourceGroup().location
param tags object = {}

param applicationInsightsName string = ''
param identityName string
param serviceName string = 'api-python'

param containerAppsEnvironmentName string
param containerRegistryName string

param openAICompletionDeploymentName string
param openAIEmbeddingDeploymentName string
param openAICompletionModel string
@secure()
param openAIKey string
param openAIEndpoint string
param searchServiceName string
param searchIndexName string
param searchServiceEndpoint string

resource apiGraphIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

resource search 'Microsoft.Search/searchServices@2021-04-01-preview' existing = {
  name: searchServiceName
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: applicationInsightsName
}

module app '../core/host/container-app.bicep' = {
  name: '${serviceName}-api-python'
  params: {
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': serviceName })
    identityType: 'UserAssigned'
    identityName: apiGraphIdentity.name
    containerAppsEnvironmentName: containerAppsEnvironmentName
    containerRegistryName: containerRegistryName
    containerCpuCoreCount: '1.0'
    containerMemory: '2.0Gi'
    env: [
      {
        name: 'AZURE_CLIENT_ID'
        value: apiGraphIdentity.properties.clientId
      }
      {
        name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
        value: applicationInsights.properties.ConnectionString
      }
      {
        name: 'AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME'
        value: openAICompletionDeploymentName
      }
      {
        name: 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME'
        value: openAIEmbeddingDeploymentName
      }
      {
        name: 'AZURE_COGNITIVE_SEARCH_SERVICE_NAME'
        value: searchServiceName
      }
      {
        name: 'AZURE_COGNITIVE_SEARCH_ENDPOINT_NAME'
        value: searchServiceEndpoint
      }
      {
        name: 'AZURE_COGNITIVE_SEARCH_INDEX_NAME'
        value: searchIndexName
      }
      {
        name: 'AZURE_COGNITIVE_SEARCH_API_KEY'
        value: search.listAdminKeys().primaryKey
      }
      {
        name: 'AZURE_TENANT_ID'
        value: apiGraphIdentity.properties.tenantId
      }
      {
        name: 'OPENAI_COMPLETION_MODEL'
        value: openAICompletionModel
      }
      {
        name: 'OPENAI_API_VERSION'
        value: '2023-05-15'
      }
      {
        name: 'OPENAI_API_BASE'
        value: openAIEndpoint
      }
      {
        name: 'OPENAI_API_KEY'
        value: openAIKey
      }
      {
        name: 'OPENAI_API_TYPE'
        value: 'azure'
      }
    ]
    targetPort: 5291
  }
}


output SERVICE_API_PYTHON_IDENTITY_PRINCIPAL_ID string = apiGraphIdentity.properties.principalId
output SERVICE_API_PYTHON_NAME string = app.outputs.name
output SERVICE_API_PYTHON_URI string = app.outputs.uri
output SERVICE_API_PYTHON_IMAGE_NAME string = app.outputs.imageName
