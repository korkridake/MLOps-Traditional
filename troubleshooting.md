# Troubleshooting

## Installation Error Streamlit: Building wheel for pyarrow (pyproject.toml)

### Symptoms

 I get errors and I can't get it to work when installing the package within the requirement file.

### Cause

- pyarrow doesn't support Python 3.11 yet (here is the PR in pyarrow's github, it'll arrive in the next release).

### Resolution

- [python - Installation error streamlit: Building wheel for pyarrow (pyproject.toml) ... error - Stack Overflow](https://stackoverflow.com/questions/74254073/installation-error-streamlit-building-wheel-for-pyarrow-pyproject-toml-er)

## MLFlow's Conflicting Dependencies

### Symptoms

To be added

### Cause

The conflict is caused by:

- The user requested pyarrow==14.0.0
- mlflow 2.6.0 depends on pyarrow<13 and >=4.0.0
- MLflow 2.8.0 specifically requires `pyarrow<14,>=4.0.0`.

### Resolution

To fix this you could try to:

1. Loosen the range of package versions you've specified
2. Remove package versions to allow pip to attempt to solve the dependency conflict
3. [[BUG] Security Vulnerability · Issue #10413 · mlflow/mlflow](https://github.com/mlflow/mlflow/issues/10413)

## Storage Account Doesn't Permit Key-Based Authentication

### Symptoms

Met error <class 'Exception'>:KeyBasedAuthenticationNotPermitted
Operation returned an invalid status 'Key based authentication is not permitted on this storage account.'
This SAS token is derived from an account key, but key-based authentication is not permitted for this storage account. To update workspace properties, please see the documentation: https://review.learn.microsoft.com/azure/machine-learning/how-to-disable-local-auth-storage?view=azureml-api-2&branch=pr-en-us-278974&tabs=cli#update-an-existing-workspace
Please check log by running the command with '--debug' for more details.

### Cause

To be added

### Resolution

To be added