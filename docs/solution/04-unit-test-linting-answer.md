# Azure MLOps Challenge Blog: Part 5 - Arinco
In my [previous post](https://arinco.com.au/blog/azure-mlops-challenge-part-4/), we walked through the steps to complete the fourth module of the Azure MLOps Challenge which was the implement feature branching and configure our GitHub Action workflow to trigger when a pull request is raised. In this post,  I will show you how to complete the fith module of the Azure MLOps Challenge. We’ll update our GitHub Actions workflow to run unit tests and linting on our code.

This content is based on Challenge 4 of the MLOps Challenge Labs. I’ll provide an overview of the key concepts and my solution to the challenge. If you want to follow along yourself, you can find instructions at the MLOps challenge documentation site: [https://microsoftlearning.github.io/mslearn-mlops/documentation/04-unit-test-linting.html](https://microsoftlearning.github.io/mslearn-mlops/documentation/04-unit-test-linting.html)

Here is a brief description of technologies you’ll encounter in this challenge, that weren’t covered in the previous blog/s.

*   MLSecOps: is a new and emerging field that aims to integrate security, devops and machine learning practices. It is based on the idea that machine learning systems and models pose unique security challenges and risks that need to be addressed throughout the machine learning lifecycle. MLSecOps provides a framework and a set of standards for testing, verifying, and deploying secure and responsible machine learning solutions at scale. MLSecOps also helps to automate and streamline the collaboration between developers, operations teams, and security experts in the context of machine learning projects. You can learn more about MLSecOps from the following resources: [https://owasp.org/www-project-mlsecops-verification-standard/#](https://owasp.org/www-project-mlsecops-verification-standard/#)

Although unit testing and linting are just the tip of the iceberg when it comes to DevSecOps or MLSecOps, they are a good place to start, I’ll also be adding in dependency checking  to the workflow, which is a tool that checks for known vulnerabilities in your pip libraries.

We’ve got long one today so let’s get started! 🚀

**Challenge 4: Work with linting and unit testing**
---------------------------------------------------

The Objectives of the fifth challenge are as follows:

*   Run linters and unit tests with GitHub Actions.
*   Troubleshoot errors to improve your code.

The linting, unit testing and Github Action yml file have been provided for us. As instructed, we’ll run the “Code checks” workflow manually to see if it passes. We can do this by clicking on the “Actions” tab in our GitHub repo and then clicking on the “Code checks” workflow. We can then click on the “Run workflow” button to run the workflow manually.

The unit test contains three test cases:

*   `test_csvs_no_files`: This test case checks that the `get_csvs_df` function raises a `RuntimeError` with the expected error message when it is called with a path that does not contain any CSV files.
*   `test_csvs_no_files_invalid_path`: This test case checks that the `get_csvs_df` function raises a `RuntimeError` with the expected error message when it is called with an invalid path that does not exist.
*   `test_csvs_creates_dataframe`: This test case checks that the `get_csvs_df` function correctly creates a DataFrame when it is called with a valid path that contains CSV files. The test case uses the `os.path` module to construct the path to a `datasets` directory, which should contain the CSV files to be loaded. The test case then calls the `get_csvs_df` function with this path and checks that the resulting DataFrame has the expected number of rows.

Lucky for us, the only error we get is that some lines are too long. 👌

![](https://arinco.com.au/wp-content/uploads/2023/09/image-15-1024x728.png)

We can resolve this by adding extra lines to our code and pushing up the changes. Here’s an example of what I did:

```
def split_data(df, test_size=0.2):
    # split data into train and test sets
    X = df.drop("Diabetic", axis=1)
    y = df["Diabetic"]
    X_train, X_test, y_train, y_test = train_test_split(
        #new line
        X, y, test_size=test_size)
    return X_train, X_test, y_train, y_test

```


Running the workflow again, we can see that it passes.

![MLOps](https://arinco.com.au/wp-content/uploads/2023/09/image-17-1024x515.png)

Taking the yml code provided in `04-unit-test-linting.yml` let’s add it to our existing workflow file `02-manual-trigger-job.yml`, we’ll also add a job for unit testing, and to take it a step further we’ll add in a manual approval job to the workflow. I’ve tied all the steps together by using the `needs: [job]` dependancy so each step requires the previous step to pass before it can run.

To support the manual approval, I created a new environment in GitHub called “dev” and added myself as a reviewer.

![](https://arinco.com.au/wp-content/uploads/2023/09/image-18-1024x868.png)

We’ll also have to add a new “Federated credential scenario” to the Azure AD service principal. This is because the GitHub Action workflow will use the environment context for authentication over the pull-request context we created initially.

![](https://arinco.com.au/wp-content/uploads/2023/09/image-28-1024x1006.png)

The final workflow file should something look like this:

```
name: Deploy

on:
  workflow_dispatch:
  pull_request:
    branches: [main]

env:
  workspace-name: myWorkspace # name of the Azure Machine Learning workspace
  resource-group: myResourceGroup # name of the Azure resource group

permissions:
  id-token: write
  contents: read

jobs:
  linting:
    name: linting
    runs-on: ubuntu-latest
    steps:
    - name: Check out repo
      uses: actions/checkout@main
    - name: Use Python version 3.8
      uses: actions/setup-python@v3
      with:
        python-version: '3.8'
    - name: Install Flake8
      run: |
        python -m pip install flake8
    - name: Run linting tests
      run: | 
        flake8 src/model/
  unit-test:
    name: unit-test
    runs-on: ubuntu-latest
    needs: [linting]
    steps:
    - name: Check out repo
      uses: actions/checkout@main
    - name: Use Python version 3.8
      uses: actions/setup-python@v3
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt 
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - name: Run unit tests
      run: | 
        pytest tests/test_train.py
  train:
    runs-on: ubuntu-latest
    needs: [unit-test]
    environment: 
      name: dev
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
        run: az ml job create --file src/job.yml --workspace-name ${{ env.workspace-name }} --resource-group ${{ env.resource-group }}

```


We can see our linting and unit testing jobs have passed, and we can see the manual approval job is waiting for approval.

![](https://arinco.com.au/wp-content/uploads/2023/09/image-19-930x1024.png)

![](https://arinco.com.au/wp-content/uploads/2023/09/image-20-1024x413.png)

Clicking “Review pending deployments” we can approve the deployment.

![](https://arinco.com.au/wp-content/uploads/2023/09/image-21.png)

There are many, many different ways to manage approvals, but this is a simple solution to get started. Some examples of other manual approvals methods are:

    – Adding specific labels or key words to the PR.

    – Sending requests to Teams or Slack channels.

    – Approving requests in vsCode GitHub Pull Request extension.

Another good idea is to add “Require status checks to pass before merging” to your branch protection rules. This will ensure that the jobs have passed before the PR can be merged.

![](https://arinco.com.au/wp-content/uploads/2023/09/image-22-1024x912.png)

We’ve now got a fully automated workflow that runs linting, unit testing and a manual approval before deploying our model to Azure Machine Learning. 🚀

![](https://arinco.com.au/wp-content/uploads/2023/09/image-23.png)

To turn things up to 11, let’s add in [Snyk](https://snyk.io/) to our workflow. Snyk is a tool that checks for known vulnerabilities in your code, pip dependencies, containers and IaC. GitHub has in-built functionality for dependecy scanning called DependaBot, but this a good oppertunity to work with something new.

After registering for a free account and retrieving the API key, add a new environment variable to your repo secrets called \`SNYK\_TOKEN\` and paste in the API key.

![](https://arinco.com.au/wp-content/uploads/2023/09/image-24-1024x805.png)

To add Snyk to our GitHub Action workflow we’ll need to add a new \`secuirty\` job to our workflow yaml.

```
name: Deploy

on:
  workflow_dispatch:
  pull_request:
    branches: [main]

env:
  workspace-name: myWorkspace # name of the Azure Machine Learning workspace
  resource-group: myResourceGroup # name of the Azure resource group

permissions:
  id-token: write
  contents: read

jobs:
  linting:
    name: linting
    runs-on: ubuntu-latest
    steps:
    - name: Check out repo
      uses: actions/checkout@main
    - name: Use Python version 3.8
      uses: actions/setup-python@v3
      with:
        python-version: '3.8'
    - name: Install Flake8
      run: |
        python -m pip install flake8
    - name: Run linting tests
      run: | 
        flake8 src/model/
  unit-test:
    name: unit-test
    runs-on: ubuntu-latest
    needs: [linting]
    steps:
    - name: Check out repo
      uses: actions/checkout@main
    - name: Use Python version 3.8
      uses: actions/setup-python@v3
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt 
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - name: Run unit tests
      run: | 
        pytest tests/test_train.py
  security: # new job for Snyk
    runs-on: ubuntu-latest
    needs: [unit-test]
    name: Snyk scan
    steps:
      - uses: actions/checkout@master
      - name: Snyk scan
        uses: snyk/actions/python-3.8@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
  train:
    runs-on: ubuntu-latest
    needs: [security]
    environment: 
      name: dev
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
        run: az ml job create --file src/job.yml --workspace-name ${{ env.workspace-name }} --resource-group ${{ env.resource-group }}

```


After pushing the code up to the branch associated with our pull request, we can see that the Snyk job has failed. 😂

![](https://arinco.com.au/wp-content/uploads/2023/09/image-25-829x1024.png)

This is a particularly interesting one to fix, as there’s no upgrade or patch available (at time of writing). To add an exception to the Snyk check, we’ll need to add a policy file to our repo.

Create a new file called `.snyk` in the root of your repo and add the following code:

```
# Snyk (https://snyk.io) policy file, patches or ignores known vulnerabilities.
version: v1.22.0
# ignores vulnerabilities until expiry date; change duration by modifying expiry date
ignore:
  SNYK-PYTHON-MLFLOW-5811861:
    - '* > mlflow':
        reason: no upgrade available
        expires: '2023-08-29T11:54:16.639Z'
patch: {}

```


Commit and push the changes one final time and we can see that the Snyk job has passed.

![](https://arinco.com.au/wp-content/uploads/2023/09/image-26-1024x628.png)

![](https://arinco.com.au/wp-content/uploads/2023/09/image-27-969x1024.png)

![](https://arinco.com.au/wp-content/uploads/2023/09/image-29.png)

**Conclusion**
--------------

In this post, we walked through the steps to successfully complete the fifth module of the Azure MLOps Challenge which was to update our GitHub Actions workflow to run unit tests and linting on our code. We also added in a manual approval step and a Snyk job to check for known vulnerabilities in our pip dependencies.

In the next post, we’ll walk through the steps to complete the sixth module of the Azure MLOps Challenge which is to create a new production environment in GitHub and deploy a new version of our model.

Happy learning and good luck! 🚀