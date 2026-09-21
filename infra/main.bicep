// ============================================================================
// Azure Cloud Resume Challenge — Infrastructure as Code (Step 12)
//
// Provisions the complete backend stack:
//   1. Cosmos DB Account (Serverless, Table API)
//   2. Cosmos DB Table (VisitorCounter)
//   3. Storage Account (required by Azure Functions runtime)
//   4. App Service Plan (Consumption / Serverless, Linux)
//   5. Function App (Python 3.12, Linux) with Cosmos DB connection injected
// ============================================================================

// ---------------------------------------------------------------------------
// Parameters
// ---------------------------------------------------------------------------

@description('Azure region for all resources.')
param location string = 'japaneast'

@description('Name of the Cosmos DB account.')
param cosmosDbAccountName string = 'jdmcosmosresume'

@description('Name of the Cosmos DB table.')
param cosmosDbTableName string = 'VisitorCounter'

@description('Name of the Storage Account used by Azure Functions.')
param funcStorageAccountName string = 'jdmcloudfuncst'

@description('Name of the App Service Plan (Consumption).')
param appServicePlanName string = 'asp-cloud-resume'

@description('Name of the Azure Function App.')
param functionAppName string = 'func-cloud-resume-jdm'

// ---------------------------------------------------------------------------
// 1. Cosmos DB Account — Serverless, Table API
// ---------------------------------------------------------------------------
resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: cosmosDbAccountName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    capabilities: [
      { name: 'EnableTable' }       // Enables Table API
      { name: 'EnableServerless' }  // Serverless capacity mode
    ]
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    backupPolicy: {
      type: 'Periodic'
      periodicModeProperties: {
        backupIntervalInMinutes: 240
        backupRetentionIntervalInHours: 8
        backupStorageRedundancy: 'Local'
      }
    }
  }
}

// ---------------------------------------------------------------------------
// 2. Cosmos DB Table — VisitorCounter
// ---------------------------------------------------------------------------
resource cosmosDbTable 'Microsoft.DocumentDB/databaseAccounts/tables@2024-05-15' = {
  parent: cosmosDbAccount
  name: cosmosDbTableName
  properties: {
    resource: {
      id: cosmosDbTableName
    }
  }
}

// ---------------------------------------------------------------------------
// 3. Storage Account — Required by Azure Functions for internal operations
// ---------------------------------------------------------------------------
resource funcStorageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: funcStorageAccountName
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

// ---------------------------------------------------------------------------
// 4. App Service Plan — Consumption (Serverless) for Linux
// ---------------------------------------------------------------------------
resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: appServicePlanName
  location: location
  kind: 'linux'
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  properties: {
    reserved: true  // Required for Linux hosting
  }
}

// ---------------------------------------------------------------------------
// 5. Function App — Python 3.12 on Linux with Cosmos DB connection injected
// ---------------------------------------------------------------------------
resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: appServicePlan.id
    reserved: true
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'Python|3.12'
      pythonVersion: '3.12'
      appSettings: [
        // Azure Functions runtime settings
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${funcStorageAccount.name};AccountKey=${funcStorageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        // Cosmos DB Table API connection string — index [4] is "Primary Table Connection String"
        // (index [0] is the SQL connection string, which is incompatible with azure-data-tables SDK)
        {
          name: 'COSMOS_DB_CONNECTION_STRING'
          value: cosmosDbAccount.listConnectionStrings().connectionStrings[4].connectionString
        }
      ]
      cors: {
        allowedOrigins: [
          'https://jdmercado.site'
          'https://www.jdmercado.site'
          'https://portal.azure.com'
        ]
        supportCredentials: false
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Outputs — Useful references after deployment
// ---------------------------------------------------------------------------

@description('The deployed Function App default hostname.')
output functionAppHostname string = functionApp.properties.defaultHostName

@description('The full API endpoint URL for GetResumeCounter.')
output apiEndpoint string = 'https://${functionApp.properties.defaultHostName}/api/GetResumeCounter'

@description('The Cosmos DB account endpoint.')
output cosmosDbEndpoint string = cosmosDbAccount.properties.documentEndpoint
