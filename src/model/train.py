"""Train a logistic regression model using data from CSV files."""

import argparse
import glob
import os
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from mlflow.sklearn import autolog

def main(arguments):
    """Main function to run the training pipeline."""
    autolog()
    df = get_csvs_df(arguments.training_data)
    x_train, x_test, y_train, y_test = split_data(df)
    train_model(arguments.reg_rate, x_train, y_train)

def get_csvs_df(path):
    """Read and concatenate all CSV files in the given directory."""
    if not os.path.exists(path):
        raise RuntimeError(f"Cannot use non-existent path provided: {path}")
    csv_files = glob.glob(f"{path}/*.csv")
    if not csv_files:
        raise RuntimeError(f"No CSV files found in provided data path: {path}")
    return pd.concat((pd.read_csv(f) for f in csv_files), sort=False)

def split_data(df, test_size=0.2):
    """Split the dataframe into train and test sets."""
    x = df.drop("Diabetic", axis=1)
    y = df["Diabetic"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size
    )
    return x_train, x_test, y_train, y_test

def train_model(reg_rate, x_train, y_train):
    """Train a logistic regression model."""
    LogisticRegression(C=1 / reg_rate, solver="liblinear").fit(x_train, y_train)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--training_data", dest="training_data", type=str)
    parser.add_argument("--reg_rate", dest="reg_rate", type=float, default=0.01)
    return parser.parse_args()

if __name__ == "__main__":
    print("\n\n")
    print("*" * 60)
    args = parse_args()
    main(args)
    print("*" * 60)
    print("\n\n")