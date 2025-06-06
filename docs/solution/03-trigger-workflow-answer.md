# Azure MLOps Challenge Blog: Part 4 - Arinco
In [my previous post](https://arinco.com.au/blog/azure-mlops-challenge-part-3/) on the Azure MLOps Challenge, I walked through the steps to create a service principal using the Azure CLI and used OpenID Connect to authenticate GitHub to Azure AD (Entra ID). Additionally, we configured a yaml GitHub Workflow to trigger the Azure ML job manually.

In this short blog post, I will show you how to complete the fourth module of the challenge, which is to trigger GitHub Actions with feature-based branching. Feature-based branching is a software development practice that involves creating and testing new features in separate branches before merging them into the main branch. This way, you can isolate and validate each feature independently, and avoid breaking the existing functionality.

The content is based on Challenge 3 of the MLOps Challenge Labs. I’ll provide an overview of the key concepts and my solution to the challenge. If you want to follow along yourself, you can find instructions at the MLOps challenge documentation site: [https://microsoftlearning.github.io/mslearn-mlops/documentation/03-trigger-workflow.html](https://microsoftlearning.github.io/mslearn-mlops/documentation/03-trigger-workflow.html)

Here is a brief description of technologies you’ll encounter in this challenge, that weren’t covered in the previous blog/s.

*   Branch protection rules: are a way to enforce certain workflows or requirements before a collaborator can push changes to a branch in a repository, including merging a pull request into the branch. By default, there are no branch protection rules in GitHub, meaning that anyone with write access can modify any branch. However, you can create a branch protection rule for a specific branch, all branches, or any branch that matches a name pattern you specify with wildcard syntax. By creating a branch protection rule, you can disable force pushes and prevent the branch from being deleted. You can also enable additional settings, such as requiring reviews, successful status checks, signed commits, linear history, etc. You can apply the restrictions to administrators and roles with the “bypass branch protections” permission. You can manage branch protection rules using the GitHub web interface or the GitHub API.

The goal of this module is to create branch protection policy on the main branch of our GitHub repository and configure a GitHub Actions workflow that will trigger the Azure ML job when a pull request is raised.

Let’s get started! 🚀

**Challenge 3: Trigger the Azure Machine Learning job with GitHub Actions**
---------------------------------------------------------------------------

The Objectives of the fourth challenge are as follows:

*   Work with feature-based development.
*   Protect the main branch.
*   Trigger a GitHub Actions workflow by creating a pull request.

First up, we want to remove the Open ID Connect authentication to the main brach from our service principal. This is because we want to trigger the Azure ML job when a pull request is raised, and we can’t do that with Open ID Connect authentication as it’s currently configured.

Delete the original Federated Credential from the service principal and add a new one for pull requests. You can use the Portal or modify the JSON file from the previous blog. The end result should look like this:

![Azure MLOps](https://arinco.com.au/wp-content/uploads/2023/08/image-12-1024x437.png)

Next, head over to the GitHub repository and creating protection policy on the main branch.

This is under Settings > Branches > Add rule

![](https://arinco.com.au/wp-content/uploads/2023/08/image-8-933x1024.png)

For the purposes of this learning exercise we’ll leave “require approvals” unchecked. However, in a real-world scenario, you would want to require **\*\*at least\*\*** one approval before merging a pull request into the main branch.

With our branch protection policy in place, we can now update `02-manage-aml-workspace.yml` to trigger the Azure ML job when a pull request is raised.

All that requires is adding the following code to the workflow file:

```
on:
  # existing code  
  workflow_dispatch:
  # new code
  pull_request:
    branches: [main]

```


Let’s create a new branch for our workflow:

```
git checkout -b new-branch

```


Now we’ll commit our changes and push them to the remote repository:

```
git commit -am "update workflow"

```


* * *

_**git commit -m** is used to add all tracked changes to the Git working repository._

_**git commit -am** automatically adds the tracked and untracked changes to the Git repository._

* * *

Now we can create a pull request to merge our changes into the main branch.

Under the “Pull requests” tab, click “New pull request” and select the “new-branch” branch as the source branch and the “main” branch as the target branch.

![](https://arinco.com.au/wp-content/uploads/2023/08/image-9-1024x479.png)

![](https://arinco.com.au/wp-content/uploads/2023/08/image-10-1024x479.png)

We can see our job has been triggered and is running in the Pull Request Checks section.

![](https://arinco.com.au/wp-content/uploads/2023/08/image-11-1024x466.png)

After a few minutes, we can verify that the job has completed successfully.

![](https://arinco.com.au/wp-content/uploads/2023/08/image-13-1024x527.png)

![](https://arinco.com.au/wp-content/uploads/2023/08/image-14-1024x401.png)

![](https://arinco.com.au/wp-content/uploads/2023/08/image-16-1024x527.png)

**Conclusion**
--------------

In this post, we walked through the steps to successfully complete the fourth module of the Azure MLOps Challenge. We created a branch protection policy on the main branch of our GitHub repository and configured a GitHub Actions workflow that will trigger the Azure ML job when a pull request is raised.

In the next post, we’ll take on the fifth module where we step it up a gear and enter the realm of MLSecOps, adding linting and unit testing to our GitHub Actions workflow. Stay tuned! 📺