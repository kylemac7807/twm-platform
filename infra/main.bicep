// TWM development environment: first two pieces (documents and secrets).
// NOT YET VALIDATED: written Nov 22, 2026 before the Bicep tool was installed on Kyle's machine. Validate with
// `az bicep build --file infra/main.bicep` in the first Azure session (docs/azure-first-session.md) before any deployment.
// Deployed into one resource group in Canada Central by a deployment identity limited to that group; never by the owner account.

@description('Short lower-case name used in resource names, e.g. twmdev')
@minLength(3)
@maxLength(10)
param prefix string

@description('Region for everything; Canada Central from the start (decided Oct 6, 2026)')
param location string = 'canadacentral'

@description('Object ID of the deployment identity that may read and write secrets')
param deployerObjectId string

var suffix = uniqueString(resourceGroup().id)

// Documents: the library and what the engine reads. No public access to blobs.
resource documents 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: toLower('${prefix}docs${take(suffix, 8)}')
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource library 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${documents.name}/default/library'
  properties: { publicAccess: 'None' }
}

// Secrets: nothing in code, nothing in the repository.
resource vault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: toLower('${prefix}kv${take(suffix, 8)}')
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: true
    enableSoftDelete: true
  }
}

// The deployment identity may manage secrets in this vault only.
resource vaultSecretsOfficer 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(vault.id, deployerObjectId, 'secrets-officer')
  scope: vault
  properties: {
    principalId: deployerObjectId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7') // Key Vault Secrets Officer
  }
}

output documentsAccount string = documents.name
output vaultName string = vault.name
