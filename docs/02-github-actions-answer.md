# Azure MLOps Challenge Blog: Part 3 - Arinco
In my [previous post on the Azure MLOps Challenge](https://arinco.com.au/blog/azure-mlops-challenge-blog-part-2/), I walked through how to create an Azure Machine Learning job using the Azure ML CLI v2. We created an Azure ML workspace, compute cluster, dataset, and job in YAML. We then used the CLI to submit the job which trained a diabetes classification model.

In this third post of the series, I will show you how to trigger the Azure ML job using GitHub Actions. GitHub Actions allows you to automate your workflow by triggering jobs based on events in your GitHub repository.

Here is a brief description of technologies you’ll encounter in this challenge, that weren’t covered in the previous blogs:

*   **Azure AD Service Principal**: A security identity used by applications, services, and automation tools to access specific Azure resources. In this challenge, we will create a service principal to authenticate our GitHub Action workflow with Azure ML.
*   **OpenID Connect in Azure**: An open standard and protocol that allows applications to authenticate users across different platforms. In this challenge, we will use OpenID Connect to authenticate with Azure AD.

In this blog post, I will walk you through the following steps:

*   Creating a service principal using the Azure CLI
*   Storing Azure credentials as a secret in GitHub repo
*   Configuring OpenID Connect authentication for Azure AD.

* * *

  **\*\*NOTE\*\***

This is a deviation from the challenge instructions, which uses the service principal client secret for authentication, I found OIDC to be a simpler approach and aligns with Azure best practices.

* * *

*   Configuring a GitHub Actions workflow to trigger the Azure ML job
*   Manually running the workflow to submit the job

By the end of this post we’ll be one step closer to automating our Azure Machine Learning workflow.

The content is based on Challenge 2 of the MLOps Challenge Labs. I’ll provide an overview of the key concepts and my solution to the challenge. If you want to follow along yourself, you can find instructions at the MLOps challenge documentation site: [https://microsoftlearning.github.io/mslearn-mlops/documentation/02-github-actions.html](https://microsoftlearning.github.io/mslearn-mlops/documentation/02-github-actions.html)

Let’s get started! 🚀

**Challenge 2: Trigger the Azure Machine Learning job with GitHub Actions**
---------------------------------------------------------------------------

The Objectives of the third challenge are as follows:

*   Create a service principal and use it to create a GitHub secret for authentication.
*   Run the Azure Machine Learning job with GitHub Actions.

Before updating 02-manage-aml-workspace.yml, we need to create an Azure AD application, store the details as secrets in GitHub, and configure OpenID Connect authentication in Azure AD.

To create the application, we’ll use the Azure CLI

```
az ad app create --display-name myApp
```


This command will output a JSON response with the value “**appId**” as our client-id. Next, we need to create a service principal for the application.

* * *

  **\*\*NOTE\*\***

I’ve used variables throughout this blog to keep sensitive information out of the code. You can set these variables in your terminal or in a `.env` file, or you can replace the variables with the actual values.

* * *

```
az ad sp create --id $appID
```


Replace `$appID` with the **“appId**” from the JSON output from the previous command.

Next, we’ll create a new role assignment for the service principal.

`$assigneeObjectId` is the “**id**” of the service principal. Which is in the JSON output from the **_second_** command.

`$subscriptionId` is the subscription you want to assign the role to. You can get this by running `az account show`.

`$resourceGroupName` is the name of the resource group you want to assign the role to.

In the context of this learning experience, we’re assigning the contributor role to the service principal. In a production environment, you would assign a more specific role to the service principal. Also in the effort of simplicity I’m assigning the role to the same subscription and resource group as the Azure ML workspace.

```
az role assignment create --role contributor --subscription $subscriptionId --assignee-object-id  $assigneeObjectId --assignee-principal-type ServicePrincipal --scope /subscriptions/$subscriptionId/resourceGroups/$resourceGroupName
```


Copy the values for clientId (service principal id), subscriptionId, and tenantId (appOwnerOrganizationId) to use later when we add them as encrypted secrets in our GitHub repo.

Create a file called `credential.json` with the following content:

```
{
    "name": "githubAction",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:[your GitHub account]/[your repo]:ref:refs/heads/main",
    "description": "Labs",
    "audiences": [
        "api://AzureADTokenExchange"
    ]
}
```


Here we’re using the main branch of the GitHub repository as the subject. This is to ensure that only worflows running against the main branch can authenticate to Azure to trigger the Azure ML job. There a many ways to structure this authentication scoping and we’ll explore a few different methods in this blog series.

The possible values for the subject are: repository, environment, tag, or pull request.

You can find more information and examples on OIDC here: [https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure?tabs=azure-cli%2Clinux#use-the-azure-login-action-with-openid-connect](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure?tabs=azure-cli%2Clinux#use-the-azure-login-action-with-openid-connect)

Run the following command to create a new federated identity credential for your Azure Active Directory application:

```
az ad app federated-credential create --id $assigneeObjectId --parameters credential.json
```


Now we need to create a secret in GitHub to store the clientId, subscriptionId, and tenantId.

On your repo, under Security > Secrets and variables > Actions, create a new secrets with the names AZURE\_CLIENT\_ID, AZURE\_TENANT\_ID, and AZURE\_SUBSCRIPTION\_ID.

The result should look like this:

![MLOps](https://arinco.com.au/wp-content/uploads/2023/08/image-5-1-1024x876.png)

Finaly, let’s update azure cli login step in `02-manage-aml-workspace.yml` to use the federated (OIDC) credentials and add in a step to run the Azure ML CLI v2 command to submit the Azure ML job we created in the previous challenge. The complete file will look like this:

```
name: Manually trigger an Azure Machine Learning job

on:
  workflow_dispatch:
  pull_request:
    branches: [ main ]

env:
  workspace-name: myWorkspace # name of the Azure Machine Learning workspace
  resource-group: myResourceGroup # name of the Azure resource group

permissions:
  id-token: write
  contents: read

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
    - name: Check out repo
      uses: actions/checkout@main
    - name: Install az ml extension
      run: az extension add -n ml -y
    - name: 'Az CLI login'
      uses: azure/login@v1
      with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    - name: Trigger Azure ML job
      run: az ml job create --file src/job.yml --workspace-name ${{ env.workspace-name }} --resource-group ${{ env.resource-group }}
```


For now we’ll commit our changes to the main branch and validate the workflow manually, in the following challenge we’ll add feature based banching.

```
git commit -am "updated workflow"
git push
```


After running the workflow manually we can validate the job ran successfully. 😊

![](https://arinco.com.au/wp-content/uploads/2023/08/image-6-1-1024x747.png)

And confirm the job was submitted in Azure ML Studio. (Note the “Created by” label)

![](https://arinco.com.au/wp-content/uploads/2023/08/image-7-1-1024x959.png)

**Conclusion**
--------------

In this post, we’ve created a service principal using the Azure CLI, stored Azure credentials as secrets in GitHub repo, configured OpenID Connect authentication for Azure AD, configured a GitHub Actions workflow to trigger the Azure ML job manually and validated the workflow and confirm the job was submitted successfully.

In the next post, we’ll configure a GitHub Actions workflow to run based on a pull requests.

If you are interested in joining the challenge, you can find more information and instructions on the challenge website: [https://microsoftlearning.github.io/mslearn-mlops/](https://microsoftlearning.github.io/mslearn-mlops/)

Happy learning and good luck! 🚀