import sys, os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from networksecurity.constant.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS, TARGET_COLUMN
from networksecurity.entity.artifact_entity import DataTransformationArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import  save_numpy_array_data, save_object 


class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact, data_transformation_config: DataTransformationConfig):
        try:
            self.data_validation_artifact: DataValidationArtifact = data_validation_artifact
            self.data_transformation_config: DataTransformationConfig = data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    
    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
            
    def get_data_transformer_object(self) -> Pipeline:
        try:
            # Create a KNN imputer object with the specified parameters and return a pipeline object with the KNN imputer as the first step in the pipeline
            logging.info("Creating data transformer object")
            imputer: KNNImputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info("Initializing KNN imputer with parameters: {}".format(DATA_TRANSFORMATION_IMPUTER_PARAMS))
            processor: Pipeline = Pipeline(steps=[("KNNImputer", imputer)])
            logging.info("Data transformer object created successfully")
            return processor
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        


        
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logging.info("Starting data transformation process")
            # Read the train and test data
            train_df = self.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = self.read_data(self.data_validation_artifact.valid_test_file_path)

            # Separate input features and target feature from training and testing data
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN])
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_train_df = target_feature_train_df.replace(-1, 0)  # Replace -1 with 0 in the target feature

            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN])
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1, 0)  # Replace -1 with 0 in the target feature

        
            preprocessor = self.get_data_transformer_object()
            preprocessor_object = preprocessor.fit(input_feature_train_df)
            transformed_input_feature_train_df = preprocessor_object.transform(input_feature_train_df)
            transformed_input_feature_test_df = preprocessor_object.transform(input_feature_test_df)

            train_arr = np.c_[transformed_input_feature_train_df, np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_feature_test_df, np.array(target_feature_test_df)]

            # Save the transformed data
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, test_arr)
            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor_object)

            

            # Create and return the data transformation artifact
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path,
                )

            logging.info("Data transformation completed successfully")
            return data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e