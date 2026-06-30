from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import SAVED_MODEL_DIR, SAVED_MODEL_FILE_NAME

import os, sys


class NetworkSecurityModel:
    def __init__(self, preprocessing_object, trained_model_object):
        """
        TrainedModel constructor

        preprocessing_object: preprocessing_object
        trained_model_object: trained_model_object
        """
        self.preprocessing_object = preprocessing_object
        self.trained_model_object = trained_model_object

    def predict(self, X):
        """
        function accepts raw inputs and then transformed raw input using preprocessing object and then it does prediction on transformed features
        """
        try:
            X_transform = self.preprocessing_object.transform(X)
            y_hat = self.trained_model_object.predict(X_transform)
            return y_hat
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e