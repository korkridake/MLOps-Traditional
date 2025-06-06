# Azure MLOps Challenge Blog: Part 7 - Arinco
Hello again! 👋

In [my previous post](https://arinco.com.au/blog/azure-mlops-challenge-blog-part-6/) we created a new `prod` environment in our GitHub repo, added a required reviewer and added our Azure credentials as Environment secrets. Lastly we created a new dataset in Azure Macine Learning and added new training job in our GitHub Actions workflow to trigger the `prod` training job.

In this post we’ll walk through the steps to complete of the seventh and _**final**_ module of the [Azure MLOps Challenge](https://microsoftlearning.github.io/mslearn-mlops/documentation/06-deploy-model.html). 🥳 We’ll use Github Actions to register and deploy our model to an online endpoint and test the deployed model using Azure Machine Learning CLI v2.

Let’s get started! 🚀

**Challenge 6: Deploy and test the model**
------------------------------------------

The Objectives of the sixth challenge are as follows:

*   Register the model with GitHub Actions.
*   Deploy the model to an online endpoint with GitHub Actions.
*   Test the deployed model.

To keep things simple we’ll deploy the model to a managed online endpoint and let Azure abstract away the underlying compute resources. In a production environment you would look to deploy the model to an Azure Kubernetes Service (AKS) cluster and in a larger Dev or UAT environment might would look to deploy the model to an Azure Container Instance (ACI) cluster.

Before we can deploy the model we need to register the model with Azure Machine Learning. We’ll create a new model from the output of the production training job. To get our bearings, let’s take a look at the output of the production training job:

![](https://arinco.com.au/wp-content/uploads/2023/09/image-33-1024x474.png)

we can get the same information from the GitHub workflow output:

![](https://arinco.com.au/wp-content/uploads/2023/09/image-34-1024x890.png)

The most important thing here this is the Job Name/ID. We’ll use this to register the model with Azure Machine Learning.

We also need to create two yaml files to support the creation of the endpoint and the deployment of the model to said endpoint.

Create a new `create-endpoint.yml` file in the `src` folder with the following code:

```
$schema: https://azuremlschemas.azureedge.net/latest/managedOnlineEndpoint.schema.json
name: mlflow-endpoint-unique # Name of the endpoint - must be unique within the Azure Region
auth_mode: key # Authentication mode for the endpoint

```


Create a new `deploy-endpoint.yml` file in the `src` folder with the following code:

```
$schema: https://azuremlschemas.azureedge.net/latest/managedOnlineDeployment.schema.json
name: mlflow-deployment
endpoint_name: mlflow-endpoint # Name of the endpoint to deploy the model to
model: azureml:my-model:1
instance_type: Standard_DS3_v2
instance_count: 1

```


One thing to note here: since we’re using MLflow we don’t need to provide a scoring script or specify the environment.

After building out the jobs and steps required, you end up with the following GitHub Actions workflow. I played around with a few different ways to stucture the Github Actions workflow to deploy the endpoint and the model. I landed on pull request labels. This allow’s us to retain the existing process of having the `dev` and `prod` models train automatically in the “main” workflow when a pull requested is opened and then have the model deployed in a separate workflow when a label is added to the pull request. This also accomidates separate workflows for the `dev` and `prod` models.

```
name: Deploy Model

on:
  pull_request_target:
    types: [labeled]

env:
  workspace-name: myWorkspace # name of the Azure Machine Learning workspace
  resource-group: myResourceGroup # name of the Azure resource group
  job-name: lime_queen_k194g7dtrk # name of the job that contains the model
  model-name: my-model # name of the model

permissions:
  id-token: write
  contents: read

jobs:
  register-model:
    if: github.event.label.name == 'register-model'
    name: Register Model
    runs-on: ubuntu-latest
    environment:
      name: prod
    steps:
      - name: Check out repo
        uses: actions/checkout@main
      - name: Install az ml extension
        run: az extension add -n ml -y
      - name: "Az CLI login"
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Trigger Azure ML job
        run: az ml model create --name ${{ env.model-name }} --path azureml://jobs/${{ env.job-name }}/outputs/artifacts/paths/model/ --type mlflow_model --workspace-name ${{ env.workspace-name }} --resource-group ${{ env.resource-group }}
  create-endpoint:
    name: Create Endpoint
    if: github.event.label.name == 'create-endpoint'
    runs-on: ubuntu-latest
    environment:
      name: prod
    steps:
      - name: Check out repo
        uses: actions/checkout@main
      - name: Install az ml extension
        run: az extension add -n ml -y
      - name: "Az CLI login"
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Trigger Azure ML job
        run: az ml online-endpoint create -f src/create-endpoint.yml --workspace-name ${{ env.workspace-name }} --resource-group ${{ env.resource-group }}
  deploy-model:
    name: Deploy Model
    if: github.event.label.name == 'deploy-model'
    runs-on: ubuntu-latest
    environment:
      name: prod
    steps:
      - name: Check out repo
        uses: actions/checkout@main
      - name: Install az ml extension
        run: az extension add -n ml -y
      - name: "Az CLI login"
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Trigger Azure ML job
        run:  az ml online-deployment create -f src/deploy-endpoint.yml --all-traffic --workspace-name ${{ env.workspace-name }} --resource-group ${{ env.resource-group }}

```


For the purposed of readability I’ve kept the environment variables at the top of the the workflow. You could store these values in a seperate parameter files, GitHub Secrets, GitHub Actions environment/repo variables even in Azure Configuration Manager. Ideally you would programatically pull these values from the Azure Machine Learning workspace and register the model with the Azure Machine Learning workspace directly after training.

I’ve setup the workflow to trigger when a pull request is opened and when a label is added to the pull request. The workflow will trigger the `register-model` job when the `register-model` label is added to the pull request. The workflow will trigger the `create-endpoint` job when the `create-endpoint` label is added to the pull request. The workflow will trigger the `deploy-model` job when the `deploy-model` label is added to the pull request.

After commiting and pushing our changes we can add the labels to the pull request and watch the magic happen! 🪄

![](https://arinco.com.au/wp-content/uploads/2023/09/image-35-1024x896.png)

![](https://arinco.com.au/wp-content/uploads/2023/09/image-36-811x1024.png)

Because this is part of of the prod environment this WILL prompt for approval before deploying the model. This is a good thing! 👍

With the label workflow structre you have to add one label, let the job complete and then add the next label. Adding all the labels at once will cause the workflow to fail because the jobs will in parralel and the `deploy-model` job will fail because the model hasn’t been registered or the endpoint hasn’t been created. The advantage of this approach is the can re-run individual jobs in isolation as needed. For example, if you register a new version of a model, or yoy want to deploy and endpoint with more compute resources.

After the model has been successfuly deployed we can move onto the final step of the challenge: testing the deployed model.

![](https://arinco.com.au/wp-content/uploads/2023/09/image-37-726x1024.png)

We’ll do the testing with the CLI for now. But we’ll do something more exiting in the next post. 🤫

To test the model convert the provided data to JSON and run the following command:

```
{
  "input_data": {
    "columns": [
      "PatientID",
      "Pregnancies",
      "PlasmaGlucose",
      "DiastolicBloodPressure",
      "TricepsThickness",
      "SerumInsulin",
      "BMI",
      "DiabetesPedigree",
      "Age"
    ],
    "index": [0, 1, 2],
    "data": [
      [1, 9, 104, 51, 7, 24, 27.36983156, 1.350472047, 43],
      [2, 6, 73, 61, 35, 24, 18.74367404, 1.074147566, 75],
      [3, 4, 115, 50, 29, 243, 34.69215364, 0.741159926, 59]
    ]
  }
}

```


```
az ml online-endpoint invoke --name mlflow-endpoint-1 --request-file request.json --workspace-name myWorkspace --resource-group myResourceGroup

```


![MLOps](https://arinco.com.au/wp-content/uploads/2023/09/image-38.png)

And that’s it! 🎉 Pretty unexiting, I know. 🤣

**Conclusion**
--------------

In this post we walked through the steps to complete of the eight and _**final**_ module of the Azure MLOps Challenge. 🥳 We used Github Actions to register and deploy our model to an online endpoint and test the deployed model using Azure Machine Learning CLI v2.

In the next post we’ll create a basic flask web app and deploy the web app to Azure App Service. We’ll also create a new Github Actions pipeline to automate the deployment of the web app.

Until next time, happy coding! 👋

P.S. don’t forget to delete your Azure resources to avoid any unwanted charges. 🤑