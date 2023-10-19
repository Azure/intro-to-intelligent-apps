param name string
param location string = resourceGroup().location
param tags object = {}

param applicationInsightsName string = ''
param identityName string
param serviceName string = 'frontend'

param containerAppsEnvironmentName string
param containerRegistryName string

param backendApiUrl string

resource frontendIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: applicationInsightsName
}

module app '../core/host/container-app.bicep' = {
  name: '${serviceName}-frontend'
  params: {
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': serviceName })
    identityType: 'UserAssigned'
    identityName: frontendIdentity.name
    containerAppsEnvironmentName: containerAppsEnvironmentName
    containerRegistryName: containerRegistryName
    containerCpuCoreCount: '1.0'
    containerMemory: '2.0Gi'
    env: [
      {
        name: 'AZURE_CLIENT_ID'
        value: frontendIdentity.properties.clientId
      }
      {
        name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
        value: applicationInsights.properties.ConnectionString
      }
      {
        name: 'BACKEND_API_BASE'
        value: backendApiUrl
      }
    ]
    targetPort: 8000
  }
}

output SERVICE_FRONTEND_API_IDENTITY_PRINCIPAL_ID string = frontendIdentity.properties.principalId
output SERVICE_FRONTEND_API_NAME string = app.outputs.name
output SERVICE_FRONTEND_API_URI string = app.outputs.uri
output SERVICE_FRONTEND_API_IMAGE_NAME string = app.outputs.imageName
