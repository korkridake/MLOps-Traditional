# Azure MLOps Challenge Blog: Part 6 - Arinco
Welcome back! 🙌

In my [previous post](https://arinco.com.au/blog/azure-mlops-challenge-blog-part-5/), we successfully completed the fifth module of the Azure MLOps Challenge. We were tasked with updating our GitHub Actions workflow to run unit tests and linting on our code but we took it a step further and added manual approvals and dependency scanning with Snyk to our GitHub Actions workflow. In this post I will show you how to complete the sixth module of the Azure MLOps Challenge. We’ll add a production dataset to Azure Machine Learning and add a new training job to our GitHub Actions workflow to trigger the training of a production model. We’ll also add a new environment to our GitHub repo and add a required reviewer to the environment.

This content is based on Challenge 5 of the MLOps Challenge Labs. I’ll provide an overview of the key concepts and my solution to the challenge. If you want to follow along yourself, you can find instructions at the MLOps challenge documentation site: [https://microsoftlearning.github.io/mslearn-mlops/documentation/04-unit-test-linting.html](https://microsoftlearning.github.io/mslearn-mlops/documentation/04-unit-test-linting.html)

Here is a brief description of technologies you’ll encounter in this challenge, that weren’t covered in the previous blog/s.

*   Azure Machine Learning Environments: are a collection of resources used for model training and deployment. It contains the Python packages, environment variables, software settings and operating system that are required to run your model. You can create environments from a set of curated base images, or from your own custom Docker image. You can also create environments from a Conda specification file that defines the packages to be installed in the environment.
*   GitHub Actions Environments: provide a structured way to manage deployment targets such as production, staging, or development. The real power of environments lies in their protection rules and secrets. These rules ensure that deployments only proceed when all conditions are met, offering a secure and flexible way to manage deployment workflows. Whether you’re pushing a new feature to staging or deploying a hotfix to production, GitHub Environments has got you covered.

Let’s get started! 🚀

**Challenge 5: Work with environments**
---------------------------------------

The Objectives of the sixth challenge are as follows:

*   Set up a development and production environment.
*   Add a required reviewer.
*   Add environments to a GitHub Actions workflow.

We created the `dev` environment in the previous challenge so we can use that knowledge to create the `prod` environment using the same process including adding yourself as a required reviewer. As per the challenge instructions – we’ll add the Azure credentials directly the GitHub environment secrets and delete the repo-level secrets. This is a good practice to follow as it ensures that the secrets are only available to the GitHub Actions workflow and not to anyone with access to the repo. In a production environment you would use seperate Service Principals for each environment, scoped to the minimum permissions required in the respective Azure Subscription and/or Resource Group. In the context of our learning challenge, we’ll use the same Service Principal for both environments.

![](https://arinco.com.au/wp-content/uploads/2023/09/image-30-992x1024.png)

The next step is to add the `prod` environment to our Service Principal’s “Federated credentials” list. This is the same process we followed in the previous challenge to add the `dev` environment. The complete “Subject Identifier” should look like this:

prod: `repo:[your github account]/[your repo]:environment:prod`

dev: `repo:[your github account]/[your repo]:environment:dev`

At this point you can remove the required reviewer rule from the `dev` environment and add the Azure environment secrets if you havn’t already done so. It’s also a good idea to remove any unused credentials from the Service Principal’s “Federated credentials” list too.

Now we’ll add the `diabetes-prod-folder` to our Azure Machine Learning Workspace datasets. This is the folder that contains the `diabetes-prod.csv` file that we’ll use to create our `prod` environment. This CSV contains a larger dataset to train the model. Create a new yml file name `dataset-prod.yml` with the following contents:

```
$schema: https://azuremlschemas.azureedge.net/latest/asset.schema.json
name: diabetes-prod-folder
version: 1
path: production/data
description: Dataset pointing to diabetes-prod CSV in the repo. Data will be uploaded to default datastore.

```


The Azure Machine Learning CLI command to create the environment is:

```
az ml data create --file dataset-prod.yml --workspace-name myWorkspace --resource-group myResourceGroup 

```


A successfull json response should look like this:

```
{
  "creation_context": {
    "created_at": "2023-08-19T23:26:52.918654+00:00",
    "created_by": "",
    "created_by_type": "User",
    "last_modified_at": "2023-08-19T23:26:52.927832+00:00"
  },
  "description": "Dataset pointing to diabetes-prod CSV in the repo. Data will be uploaded to default datastore.",
  "id": "/subscriptions/[subId]/resourceGroups/myResourceGroup/providers/Microsoft.MachineLearningServices/workspaces/myWorkspace/data/diabetes-prod-folder/versions/1",
  "name": "diabetes-prod-folder",
  "path": "azureml://subscriptions/[subId]/resourcegroups/myResourceGroup/workspaces/myWorkspace/datastores/workspaceblobstore/paths/LocalUpload/386681db2f7cd59e8c96f5ee80b212db/data/",
  "properties": {},
  "resourceGroup": "myResourceGroup",
  "tags": {},
  "type": "uri_folder",
  "version": "1"
}

```


We also need to create a new yaml file for the `prod` training job in the src/model folder. This file will be called `train-prod.yml` wit the following code:

```
$schema: https://azuremlschemas.azureedge.net/latest/commandJob.schema.json
code: model
command: >-
  python train.py
  --training_data {inputs.training_data}
  --reg_rate {inputs.reg_rate}
inputs:
  training_data: 
    type: uri_folder 
    path: azureml:diabetes-prod-folder:1
  reg_rate: 0.01
environment: azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu@latest
compute: azureml:myCompute
experiment_name: diabetes-classification-production
description: Train a classification model to predict diabetes

```


We’re using the same compute target (`myCompute`) as the training job, in a production environment we would use a different compute target (cluster) to support the scale of the datasets.

Finally, we’ll add another job to the existing GitHub Actions workflow to trigger the `prod` training job. This job will look like this:

```
  train-prod:
    runs-on: ubuntu-latest
    needs: [train-dev]
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
        run: az ml job create --file src/job-prod.yml --workspace-name ${{ env.workspace-name }} --resource-group ${{ env.resource-group }} --stream # output job logs to the console

```


We’re ready to commit and push our changes! After a few minutes we’ll see the DevSecOps jobs have completed, the dev training job has completed successfully, and the prod model job is waiting for approval:

![](https://arinco.com.au/wp-content/uploads/2023/09/image-31.png)

And once all the jobs have completed finished we’ll see the following:

![](https://arinco.com.au/wp-content/uploads/2023/09/image-32.png)

**Conclusion**
--------------

In this post, we walked through the steps to meet the success critera of the sixth module of the Azure MLOps Challenge. We created a new `prod` environment in our GitHub repo, added a required reviewer and added our Azure credentials as Environment secrets. Lastly we created a new dataset in Azure Machine Learning and added new training job in our GitHub Actions workflow to trigger the `prod` training job.

In the next post, we’ll tackle the seventh and final module of the Azure MLOps Challenge which is to deploy and test our model.

Happy learning and good luck! 🚀