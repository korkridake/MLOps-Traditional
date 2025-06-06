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

To create the application, we’ll use the Azure Portal in the  following order.

1. [Authenticate to Azure from GitHub Actions by OpenID Connect | Microsoft Learn](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect)
2. [Register a Microsoft Entra app and create a service principal - Microsoft identity platform | Microsoft Learn](https://learn.microsoft.com/en-us/entra/identity-platform/howto-create-service-principal-portal#register-an-application-with-microsoft-entra-id-and-create-a-service-principal)
3. [Create a trust relationship between an app and an external identity provider - Microsoft Entra Workload ID | Microsoft Learn](https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation-create-trust?pivots=identity-wif-apps-methods-azp)

