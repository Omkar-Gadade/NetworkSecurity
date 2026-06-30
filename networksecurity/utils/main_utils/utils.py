from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV
import yaml
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import os, sys
#import dill
import pandas as pd
import numpy as np
import pickle

def read_yaml_file(file_path: str) -> dict:
    """
    Reads a YAML file and returns its contents as a dictionary.
    
    Args:
        file_path (str): The path to the YAML file.
    
    Returns:
        dict: The contents of the YAML file as a dictionary.
    """
    try:
        with open(file_path, "r") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    """
    Writes content to a YAML file.
    
    Args:
        file_path (str): The path to the YAML file.
        content (object): The content to write to the YAML file.
        replace (bool): Whether to replace the existing file. Default is False.
    
    Returns:
        None
    """
    try:
        if replace and os.path.exists(file_path):
            os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            yaml.dump(content, file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    

def save_numpy_array_data(file_path: str, array: np.array) -> None:
    """
    Saves a numpy array to a file.
    
    Args:
        file_path (str): The path to the file where the array will be saved.
        array (np.ndarray): The numpy array to save.
    
    Returns:
        None
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def load_numpy_array_data(file_path: str) -> np.array:
    """
    Loads a numpy array from a file.
    
    Args:
        file_path (str): The path to the file from which the array will be loaded.
    
    Returns:
        np.ndarray: The loaded numpy array.
    """
    try:
        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    

def save_object(file_path: str, obj: object) -> None:
    """
    Saves a Python object to a file using pickle.
    
    Args:
        file_path (str): The path to the file where the object will be saved.
        obj (object): The Python object to save.
    
    Returns:
        None
    """
    try:
        logging.info("Entered the save_object method of MainUtils class")
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)
        logging.info("Exited the save_object method of MainUtils class")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
    
def load_object(file_path: str) -> object:
    """
    Loads a Python object from a file using pickle.
    
    Args:
        file_path (str): The path to the file from which the object will be loaded.
    
    Returns:
        object: The loaded Python object.
    """
    try:
        logging.info("Entered the load_object method of MainUtils class")
        if not os.path.exists(file_path):
            raise Exception(f"The file {file_path} does not exist.")
        with open(file_path, "rb") as file_obj:
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    

def evaluate_models(X_train, y_train, X_test, y_test, models, param):
    try:
        report = {}

        for i in range(len(list(models))):
            model = list(models.values())[i]
            para = param[list(models.keys())[i]]

            gs = GridSearchCV(model,para,cv=3)
            gs.fit(X_train,y_train)

            model.set_params(**gs.best_params_)
            model.fit(X_train,y_train)

            y_train_pred = model.predict(X_train)
            
            y_test_pred = model.predict(X_test)

            train_model_score = r2_score(y_train, y_train_pred)
            test_model_score = r2_score(y_test, y_test_pred)

            report[list(models.keys())[i]] = test_model_score

            return report

    except Exception as e:
        raise NetworkSecurityException(e,sys)