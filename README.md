# Practical MLOps with GitHub Actions (Classical ML)

Welcome to the Practical MLOps with GitHub Actions repository! This project is intended to serve as the starting point for MLOps implementation in Azure, with a focus on classification problems. 

- [Practical MLOps with GitHub Actions (Classical ML)](#practical-mlops-with-github-actions-classical-ml)
  - [Project overview](#project-overview)
  - [MLOps Best Practices](#mlops-best-practices)
    - [Train Model](#train-model)
    - [Operationalize Model](#operationalize-model)
  - [Iterative-Incremental Process in MLOps](#iterative-incremental-process-in-mlops)

## Project overview

The solution accelerator provides a modular end-to-end approach for MLOps in Azure based on pattern architectures. As each organization is unique, solutions will often need to be customized to fit the organization's needs.

The solution accelerator goals are:

- Simplicity
- Modularity
- Repeatability & Security
- Collaboration
- Enterprise readiness

It accomplishes these goals with a template-based approach for end-to-end data science, driving operational efficiency at each stage. You should be able to get up and running with the solution accelerator in a few hours.

## MLOps Best Practices

### Train Model
- Data scientists work in topic branches off of master.
- When code is pushed to the Git repo, trigger a CI (continuous integration) pipeline.
- First run: Provision infra-as-code (ML workspace, compute targets, datastores).
- For new code: Every time new code is committed to the repo, run unit tests, data quality checks, train model.

We recommend the following steps in your CI process:
- **Train Model** - run training code / algo & output a [model](https://docs.microsoft.com/en-us/azure/machine-learning/concept-azure-machine-learning-architecture#model) file which is stored in the [run history](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#run).
- **Evaluate Model** - compare the performance of newly trained model with the model in production. If the new model performs better than the production model, the following steps are executed. If not, they will be skipped.
- **Register Model** - take the best model and register it with the [Azure ML Model registry](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#model-registry). This allows us to version control it.

### Operationalize Model
- You can package and validate your ML model using the **Azure ML CLI**.
- Once you have registered your ML model, you can use Azure ML + Azure DevOps to deploy it.
- You can define a **release definition** in Azure Pipelines to help coordinate a release. Using the DevOps extension for Machine Learning, you can include artifacts from Azure ML, Azure Repos, and GitHub as part of your Release Pipeline.
- In your release definition, you can leverage the Azure ML CLI's **model deploy** command to deploy your Azure ML model to the cloud (ACI or AKS).
- Define your deployment as a [gated release](https://docs.microsoft.com/en-us/azure/devops/pipelines/release/approvals/gates?view=azure-devops). This means that once the model web service deployment in the Staging/QA environment is successful, a notification is sent to approvers to manually review and approve the release. Once the release is approved, the model scoring web service is deployed to [Azure Kubernetes Service(AKS)](https://docs.microsoft.com/en-us/azure/aks/intro-kubernetes) and the deployment is tested.

## Iterative-Incremental Process in MLOps

![Iterative-Incremental Process in MLOps](media\Iterative-Incremental-Process-in-MLOps.jpg)