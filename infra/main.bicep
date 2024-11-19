targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

param openAIServiceId string
param openAIDeploymentId string
param openAIEmbeddingId string
param openAIEndpoint string
@secure()
param openAIKey string
@description('Flag that picks between csharp and python')
@allowed([
  'csharp'
  'python'
])
param backend string

param resourceGroupName string = ''
param containerAppsEnvironmentName string = ''
param containerRegistryName string = ''
param applicationInsightsName string = ''
param logAnalyticsName string = ''
param searchServiceName string = ''
param apiCsharpName string = ''
param apiPythonName string = ''
param frontendName string = ''

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Organize resources in a resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

module monitoring './core/monitor/monitoring.bicep' = {
  name: 'monitoring'
  scope: rg
  params: {
    location: location
    tags: tags
    logAnalyticsName: !empty(logAnalyticsName) ? logAnalyticsName : '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    applicationInsightsName: !empty(applicationInsightsName) ? applicationInsightsName : '${abbrs.insightsComponents}${resourceToken}'
  }
}

// Container apps host (including container registry)
module containerApps './core/host/container-apps.bicep' = {
  name: 'container-apps'
  scope: rg
  params: {
    name: 'app'
    location: location
    tags: tags
    containerAppsEnvironmentName: !empty(containerAppsEnvironmentName) ? containerAppsEnvironmentName : '${abbrs.appManagedEnvironments}${resourceToken}'
    containerRegistryName: !empty(containerRegistryName) ? containerRegistryName : '${abbrs.containerRegistryRegistries}${resourceToken}'
    logAnalyticsWorkspaceName: monitoring.outputs.logAnalyticsWorkspaceName
    applicationInsightsName: monitoring.outputs.applicationInsightsName
  }
}

module searchService 'core/search/search-services.bicep' = {
  name: 'search-service'
  scope: rg
  params: {
    name: !empty(searchServiceName) ? searchServiceName : '${abbrs.searchService}${resourceToken}'
    location: location
    tags: tags
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
    sku: {
      name: 'standard'
    }
    semanticSearch: 'free'
  }
}

var indexName = 'cognitive-search-index'
module frontend 'app/frontend.bicep' = {
  name: 'frontend'
  scope: rg
  params: {
    name: !empty(frontendName) ? frontendName : '${abbrs.appContainerApps}frontend-${resourceToken}'
    location: location
    tags: tags
    identityName: '${abbrs.managedIdentityUserAssignedIdentities}backstage-${resourceToken}'
    applicationInsightsName: monitoring.outputs.applicationInsightsName
    containerAppsEnvironmentName: containerApps.outputs.environmentName
    containerRegistryName: containerApps.outputs.registryName
    backendApiUrl: (backend == 'csharp') ? apicsharp.outputs.SERVICE_API_CSHARP_URI : apipython.outputs.SERVICE_API_PYTHON_URI
  }
}

module apicsharp 'app/api-csharp.bicep' = if (backend == 'csharp') {
  name: 'api-csharp'
  scope: rg
  params: {
    name: !empty(apiCsharpName) ? apiCsharpName : '${abbrs.appContainerApps}apicsharp-${resourceToken}'
    location: location
    tags: tags
    identityName: '${abbrs.managedIdentityUserAssignedIdentities}apicsharp-${resourceToken}'
    applicationInsightsName: monitoring.outputs.applicationInsightsName
    containerAppsEnvironmentName: containerApps.outputs.environmentName
    containerRegistryName: containerApps.outputs.registryName
    openAICompletionDeploymentName: openAIDeploymentId
    openAICompletionModel: openAIServiceId
    openAIEmbeddingDeploymentName: openAIEmbeddingId
    openAIEndpoint: openAIEndpoint
    openAIKey: openAIKey
    searchIndexName: indexName
    searchServiceEndpoint: searchService.outputs.endpoint
    searchServiceName: searchService.outputs.name
  }
}

module apipython 'app/api-python.bicep' =  if (backend == 'python') {
  name: 'api-python'
  scope: rg
  params: {
    name: !empty(apiPythonName) ? apiPythonName : '${abbrs.appContainerApps}apipython-${resourceToken}'
    location: location
    tags: tags
    identityName: '${abbrs.managedIdentityUserAssignedIdentities}backstage-${resourceToken}'
    applicationInsightsName: monitoring.outputs.applicationInsightsName
    containerAppsEnvironmentName: containerApps.outputs.environmentName
    containerRegistryName: containerApps.outputs.registryName
    openAICompletionDeploymentName: openAIDeploymentId
    openAICompletionModel: openAIServiceId
    openAIEmbeddingDeploymentName: openAIEmbeddingId
    openAIEndpoint: openAIEndpoint
    openAIKey: openAIKey
    searchIndexName: indexName
    searchServiceEndpoint: searchService.outputs.endpoint
    searchServiceName: searchService.outputs.name
  }
}

// App outputs
output APPLICATIONINSIGHTS_CONNECTION_STRING string = monitoring.outputs.applicationInsightsConnectionString
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId

output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerApps.outputs.registryLoginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerApps.outputs.registryName
