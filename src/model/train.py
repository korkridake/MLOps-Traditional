1| """Train a logistic regression model using data from CSV files."""
2| 
3| import argparse
4| import glob
5| import os
6| import pandas as pd
7| 
8| from sklearn.linear_model import LogisticRegression
9| from sklearn.model_selection import train_test_split
10| from mlflow.sklearn import autolog
11| 

12| def main(arguments):
13|     """Main function to run the training pipeline."""
14|     autolog()
15|     df = get_csvs_df(arguments.training_data)
16|     x_train, x_test, y_train, y_test = split_data(df)
17|     train_model(arguments.reg_rate, x_train, y_train)
18| 

19| def get_csvs_df(path):
20|     """Read and concatenate all CSV files in the given directory."""
21|     if not os.path.exists(path):
22|         raise RuntimeError(f"Cannot use non-existent path provided: {path}")
23|     csv_files = glob.glob(f"{path}/*.csv")
24|     if not csv_files:
25|         raise RuntimeError(f"No CSV files found in provided data path: {path}")
26|     return pd.concat((pd.read_csv(f) for f in csv_files), sort=False)
27| 

28| def split_data(df, test_size=0.2):
29|     """Split the dataframe into train and test sets."""
30|     x = df.drop("Diabetic", axis=1)
31|     y = df["Diabetic"]
32|     x_train, x_test, y_train, y_test = train_test_split(
33|         x, y, test_size=test_size
34|     )
35|     return x_train, x_test, y_train, y_test
36| 

37| def train_model(reg_rate, x_train, y_train):
38|     """Train a logistic regression model."""
39|     LogisticRegression(C=1 / reg_rate, solver="liblinear").fit(x_train, y_train)
40| 

41| def parse_args():
42|     """Parse command-line arguments."""
43|     parser = argparse.ArgumentParser()
44|     parser.add_argument("--training_data", dest="training_data", type=str)
45|     parser.add_argument("--reg_rate", dest="reg_rate", type=float, default=0.01)
46|     return parser.parse_args()
47| 

48| if __name__ == "__main__":
49|     print("\n\n")
50|     print("*" * 60)
51|     args = parse_args()
52|     main(args)
53|     print("*" * 60)
54|     print("\n\n")