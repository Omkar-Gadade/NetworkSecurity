import mlflow
import os

print("MLflow version:", mlflow.__version__)
print("Tracking URI:", mlflow.get_tracking_uri())
print("Current Working Directory:", os.getcwd())
print("USERPROFILE:", os.environ.get("USERPROFILE"))
print("HOME:", os.environ.get("HOME"))