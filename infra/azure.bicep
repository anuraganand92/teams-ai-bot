@maxLength(20)
@minLength(4)
@description('Used to generate names for all resources in this file')
param resourceBaseName string  // bot${{RESOURCE_SUFFIX}}

@description('Required when create Azure Bot service')
param botAadAppClientId string

@secure()
@description('Required by Bot Framework package in your bot project')
param botAadAppClientSecret string

@secure()
@description('Required in your bot project to access Azure OpenAI service. You can get it from Azure Portal > OpenAI > Keys > Key1 > Resource Management > Endpoint')  
param azureOpenaiKey string
param azureOpenaiModelDeploymentName string
param azureOpenaiEndpoint string
param azureOpenaiVersion string

@secure()
@description('Required in your bot project to access Azure Search service. You can get it from Azure Portal > Azure Search > Keys > Admin Key')
param azureOpenaiEmbeddingDeployment string
param azureSearchKey string
param azureSearchEndpoint string
param azureSearchIndexName string

param webAppSKU string
param linuxFxVersion string

// Newly added -- modification
@secure()
@description('Required in your bot project to access Azure Language services. You can get it from Azure Portal > Azure Language > Keys > Admin Key')
param azureLanguageKey string 
param azureLanguageEndpoint string

@maxLength(42)
param botDisplayName string

param serverfarmsName string = resourceBaseName
param webAppName string = resourceBaseName
param location string = resourceGroup().location
param pythonVersion string = linuxFxVersion

// Compute resources for your Web App
resource serverfarm 'Microsoft.Web/serverfarms@2021-02-01' = {
  kind: 'app,linux'
  location: location
  name: serverfarmsName
  sku: {
    name: webAppSKU
  }
  properties:{
    reserved: true
  }
}

// Web App that hosts your bot
resource webApp 'Microsoft.Web/sites@2021-02-01' = {
  kind: 'app,linux'
  location: location
  name: webAppName
  properties: {
    serverFarmId: serverfarm.id
    siteConfig: {
      alwaysOn: true
      appCommandLine: 'startup.sh'
      linuxFxVersion: pythonVersion
      appSettings: [
        {
          name: 'WEBSITES_CONTAINER_START_TIME_LIMIT'
          value: '600'
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        { // added
          name: 'ENABLE_ORYX_BUILD'
          value: 'true'
        }
        { // added
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: 'false'
        }
        {
          name: 'BOT_ID'
          value: botAadAppClientId
        }
        {
          name: 'BOT_PASSWORD'
          value: botAadAppClientSecret
        }
        {
          name: 'AZURE_OPENAI_API_KEY'
          value: azureOpenaiKey
        }
        {
          name: 'AZURE_OPENAI_MODEL_DEPLOYMENT_NAME'
          value: azureOpenaiModelDeploymentName
        }
        {
          name: 'AZURE_OPENAI_ENDPOINT'
          value: azureOpenaiEndpoint
        }
        { // added
          name: 'AZURE_OPENAI_VERSION'
          value: azureOpenaiVersion
        }
        {
          name: 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT'
          value: azureOpenaiEmbeddingDeployment
        }
        {
          name: 'AZURE_SEARCH_KEY'
          value: azureSearchKey
        }
        {
          name: 'AZURE_SEARCH_ENDPOINT'
          value: azureSearchEndpoint
        }
        { // added
          name: 'INDEX_NAME'
          value: azureSearchIndexName
        }
        { // added
          name: 'LANGUAGE_KEY'
          value: azureLanguageKey
        }
        { // added
          name: 'LANGUAGE_ENDPOINT'
          value: azureLanguageEndpoint
        }
      ]
      ftpsState: 'FtpsOnly'
    }
  }
}

// Register your web service as a bot with the Bot Framework
module azureBotRegistration './botRegistration/azurebot.bicep' = {
  name: 'Azure-Bot-registration'
  params: {
    resourceBaseName: resourceBaseName
    botAadAppClientId: botAadAppClientId
    botAppDomain: webApp.properties.defaultHostName
    botDisplayName: botDisplayName
  }
}

// The output will be persisted in .env.{envName}. Visit https://aka.ms/teamsfx-actions/arm-deploy for more details.
output BOT_AZURE_APP_SERVICE_RESOURCE_ID string = webApp.id
output BOT_DOMAIN string = webApp.properties.defaultHostName
