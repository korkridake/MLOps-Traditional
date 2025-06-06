# Azure MLOps Challenge Blog: Part 1 - Arinco

If you are interested in learning how to apply DevOps principles and practices to machine learning, you might want to check out the [Azure MLOps Challenge](https://microsoftlearning.github.io/mslearn-mlops/). This challenge is a hands-on learning experience that guides you through the creation and deployment of a machine learning model using Azure Machine Learning and GitHub Actions. In this blog post, I will give you an overview of the main objectives of each challenge and the solution I created to meet the success criteria.   

Unlike a regular lab that guides you through each step, a **_challenge_** lab only provides you some vague objectives and hints. You have to rely on your own abilities and ingenuity (and Github Copit 🤣) to solve the problem. This allows you to create your own unique solution and feel the thrill of discovery and the reward of creating something new.  

Join me for a series of blogs where I document my solution to each challenge, while sprinkling in a little Azure magic to take each module solution to the next level and showcase some Azure and GitHub best practice. My focus will be on the Ops side of MLOps so I won’t be concentrating on the training/evaluation of models and related Python code or other topics that would be considered the realm of Data Scientists.

What is Azure MLOps? 
---------------------

Before we dive into the details, let’s first define what MLOps is and why it matters. MLOps stands for Machine Learning Operations, and it is a set of practices that aim to improve the quality, reliability, and efficiency of machine learning workflows. MLOps borrows concepts and tools from DevOps, such as version control, continuous integration, continuous delivery, testing, monitoring, feedback loops, and adapts them to the specific needs and challenges of machine learning.   

[Azure MLOps](https://azure.microsoft.com/en-au/products/machine-learning/mlops/#features) is a solution that enables you to implement MLOps on the Azure cloud platform. It leverages Azure Machine Learning, a fully managed service that provides end-to-end capabilities for building, training, deploying, and managing machine learning models. It also integrates with GitHub Actions, a workflow automation tool that allows you to create custom pipelines for your machine learning projects. With Azure MLOps, you can streamline your machine learning lifecycle, from data preparation to model deployment and monitoring, while ensuring reproducibility, traceability, and collaboration. 

The Challenge 
--------------

The challenge consists of seven modules that cover different aspects of the machine learning lifecycle: 

*   Module 0: Convert a notebook to production code 
*   Module 1: Create an Azure Machine Learning job 
*   Module 2: Trigger the Azure Machine Learning job with GitHub Actions 
*   Module 3: Trigger GitHub Actions with feature-based development 
*   Module 4: Work with linting and unit testing 
*   Module 5: Work with environments 
*   Module 6: Deploy and test the model 

I’ll be adding an eight module to produce a functioning web app deployed to Azure App Service that will consume the model via an Azure ML Endpoint. This will be a great opportunity to showcase the power of Azure Machine Learning, GitHub Actions and Azure: 

*   Module 7: Deploy a functioning App

In each module, you will work with several technologies that are essential to implementing MLOps. Here is a brief description of each resource and its role in the challenge: 

**Workspace**: A workspace is the top-level resource for Azure Machine Learning. It is a cloud-based environment that contains all the assets and resources related to your machine learning projects, such as datasets, experiments, models, endpoints, compute targets, etc. You can create and manage workspaces using the Azure portal, the Azure Machine Learning studio, or the Azure Machine Learning CLI. A workspace also provides access to other Azure services, such as Azure Key Vault, Azure Storage, Azure Monitoring/Diagnostics, etc., that enable you to secure, store, monitor, and manage your machine learning assets. In Module 1, you will create a workspace for your challenge project. 

**Dataset**: A dataset is an abstraction that represents a data source in Azure Machine Learning. It can be created from various sources, such as local files, cloud storage, web URLs, SQL databases, etc. A dataset can be registered in a workspace for easy access and reuse across different experiments and pipelines. You can also use datasets to track data lineage and provenance. 

**Model**: A model is a file or a folder that contains the code and/or data that defines a machine learning model in Azure Machine Learning. A model can be registered in a workspace for versioning and management. You can also use models to create deployments that expose your model as a web service or an IoT module running as a Container

**Endpoint**: An endpoint is a resource that represents a deployed model in Azure Machine Learning. An endpoint consists of two components: an inference configuration and a deployment configuration. The inference configuration defines how to run the model code and what dependencies are needed. The deployment configuration defines where and how to deploy the model, such as the compute target (e.g., Azure Container Instance, Azure Kubernetes Service), the scaling options (e.g., number of instances), the authentication options (e.g., key or token), etc. You can create and manage endpoints using the Azure Machine Learning studio or the CLI. 

**Pipeline**: An Azure Machine Learning pipeline (not to be confused with an Azure DevOps pipeline) is a workflow that defines a sequence of steps to perform a complex machine learning task in Azure Machine Learning. Each step can run a script or a module on a specified compute target and produce outputs that can be consumed by subsequent steps. A pipeline can be published in a workspace for reuse and scheduling. You can also use pipelines to create GitHub Actions workflows that trigger your pipelines based on events such as code commits or pull requests. In Module 6, you will create a pipeline that automates the model training and deployment process. A pipeline has several advantages over running scripts or notebooks manually, such as: 

*   **Reproducibility**: A pipeline ensures that each step is executed with the same configuration and inputs, regardless of who runs it or when it runs. This eliminates the risk of human errors or inconsistencies that might affect the results.
*   **Modularity**: A pipeline allows you to break down a complex task into smaller and simpler steps that can be reused and combined in different ways. This makes it easier to maintain, debug, and update your code
*   **Scalability**: A pipeline enables you to run each step on a different compute target that suits its requirements, such as CPU, GPU, memory, etc. This allows you to optimize the performance and cost of your machine learning workflow.
*   **Parallelism**: A pipeline lets you run multiple steps in parallel if they do not depend on each other’s outputs. This can speed up the execution time and improve the efficiency of your machine learning workflow.
*   **Portability**: A pipeline can be exported as a JSON file that contains all the information needed to run it on another workspace or environment. This makes it easy to share and collaborate on your machine learning projects.

Preface
-------

The tone of this and future blogs in the series will be highly technical and all configuration will be complete via code. I also don’t claim that this the best or only way to complete the challenge.

To following along I recommend you have a basic understanding of the following: 

*   Core Azure resources like subscriptions, resource groups, and role-based access control 
*   Azure identity resources like Service Principals and Managed Identities 
*   Azure security solutions like Key Vault and App Configuration 
*   Version control and the CI/CD workflow 
*   Machine Learning fundamentals (how models are trained, deployed and consumed) and Azure Machine Learning Studio 
*   Python and Azure SDK’s basics like authentication and initializing clients.

Challenge 0: Convert a notebook to production code 
---------------------------------------------------

Now we’ve got to preamble out of the way, let’s get to work. 🚀 

The Objectives of the first challenge are as follows:

*   Clean nonessential code. 
*   Convert your code to Python scripts. 
*   Use functions in your scripts. 
*   Use parameters in your scripts. 

We’ll start by cloning the repo locally. 

`git clone https://github.com/MicrosoftLearning/mslearn-mlops.git` 

You can review the Jupyter notebook in the `experimentation` folder. The notebook is well commented and should be easy to follow. The notebook trains a basic regression model to predict diabetes based on several features. The notebook is based on the following tutorial: https://docs.microsoft.com/en-us/azure/machine-learning/tutorial-train-models-with-aml 

Clean nonessential code 
------------------------

As per the instructions we’ll start by adding the `split_data` function to `train.py`, you can use the `train_test_split` function from the `sklearn.model_selection` library. You can find a more examples in the following tutorial: https://learn.microsoft.com/en-gb/azure/machine-learning/how-to-convert-ml-experiment-to-production 

Add this function underneath the comment “# TO DO: add function to split data”. Make sure to also import the `train_test_split` library at the top of your script. 

```
from sklearn.model_selection import train_test_split

def split_data(df, test_size=0.2): 
    X = df.drop("Diabetic", axis=1) 
    y = df["Diabetic"] 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size) 
    return X_train, X_test, y_train, y_test 

```


Next, we’ll enable autologging with MLflow, we’ll install the mlflow library. Then, you can call `mlflow.sklearn.autolog()` before training the model to automatically log parameters, metrics, and artifacts for the scikit-learn model. Models are automatically logged when the `fit()` method is called on the pipeline object. 

The complete code should look similar to this: 

```
# Import libraries 
import argparse 
import glob 
import os 
import pandas as pd 

from sklearn.linear_model import LogisticRegression 
from sklearn.model_selection import train_test_split 
from mlflow.sklearn import autolog 

# define functions 
def main(args): 

    # enable autologging
    autolog() 

    # read data 
    df = get_csvs_df(args.training_data) 

    # split data 
    X_train, X_test, y_train, y_test = split_data(df) 

    # train model 
    train_model(args.reg_rate, X_train, X_test, y_train, y_test) 

def get_csvs_df(path): 
    if not os.path.exists(path): 
        raise RuntimeError(f"Cannot use non-existent path provided: {path}") 
    csv_files = glob.glob(f"{path}/*.csv") 
    if not csv_files: 
        raise RuntimeError(f"No CSV files found in provided data path: {path}") 
    return pd.concat((pd.read_csv(f) for f in csv_files), sort=False) 

# our new function
def split_data(df, test_size=0.2): 
    X = df.drop("Diabetic", axis=1) 
    y = df["Diabetic"] 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size) 
    return X_train, X_test, y_train, y_test 

def train_model(reg_rate, X_train, X_test, y_train, y_test): 
    # train model 
    LogisticRegression(C=1 / reg_rate, solver="liblinear").fit(X_train, y_train) 

def parse_args(): 
    # setup arg parser 
    parser = argparse.ArgumentParser() 

    # add arguments 
    parser.add_argument("--training_data", dest="training_data", type=str) 
    parser.add_argument("--reg_rate", dest="reg_rate", type=float, default=0.01) 

    # parse args 
    args = parser.parse_args() 

    # return args 
    return args 
 
# run script 
if __name__ == "__main__": 
    # add space in logs 
    print("\n\n") 
    print("*" * 60) 

    # parse args 
    args = parse_args() 

    # run main function 
    main(args) 


    # add space in logs 
    print("*" * 60) 
    print("\n\n") 

```


mlflow is already included in `requirements.txt` however, the version is very out of date and inlcudes known critical vulnerabilities. These are the versions I used: 

```
pytest==7.4.0 
mlflow==2.6.0 
pandas==2.0.3 
scikit-learn==1.3.0 

```


The completed train.py script performs the following tasks: 

*   1\. It reads in training data from a specified directory containing CSV files using the get\_csvs\_df function. 
*   2\. It splits the data into training and testing sets using the split\_data function. 
*   3\. It trains a logistic regression model using the train\_model function with a specified regularization rate. 
*   4\. It enables auto logging with MLflow to automatically log parameters, metrics, and artifacts for the scikit-learn model. 
*   5\. The script takes in two command-line arguments: –training\_data, which specifies the path to the directory containing the training data, and –reg\_rate, which specifies the regularization rate to use when training the logistic regression model. 

Conclusion
----------

In this blog post, I have given you a brief introduction to the main objectives that you will encounter in the Azure MLOps Challenge, an overview of Azure Machine Learning and the solution to Challenge 0. I hope this helps you to get started with the challenge and to learn more about how to apply MLOps principles and practices to your machine learning projects using Azure Machine Learning and GitHub Actions.  

Stay tuned for part two of this blog series we’ll tackle Challange 1 and build an Azure Machine Learning job in YAML and run an Azure Machine Learning job with the Azure Machine Learning CLIv2 

If you are interested in trying the challenge yourself, you can find more information and instructions on the challenge website: https://microsoftlearning.github.io/mslearn-mlops/ 

Happy learning and good luck! 🚀