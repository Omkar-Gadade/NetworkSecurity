from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from scipy.stats import ks_2samp
import pandas as pd
import os, sys
from networksecurity.utils.main_utils.utils import read_yaml_file
from networksecurity.utils.main_utils.utils import write_yaml_file

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            number_of_columns = len(self._schema_config["columns"])
            logging.info(f"Required number of columns: {number_of_columns}")
            logging.info(f"Actual number of columns in DataFrame: {len(dataframe.columns)}")
            if len(dataframe.columns) == number_of_columns:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def check_numerical_columns_exist(self, dataframe: pd.DataFrame) -> bool:
        try:
            numerical_columns = self._schema_config["numerical_columns"]
            dataframe_columns = dataframe.columns
            missing_numerical_columns = [col for col in numerical_columns if col not in dataframe_columns]
            if len(missing_numerical_columns) > 0:
                logging.info(f"Missing numerical columns: {missing_numerical_columns}")
                return False
            return True
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def detect_dataset_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame, threshold: float = 0.05) -> bool:
        try:
            status = True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_same_dist = ks_2samp(d1, d2)
                if threshold <= is_same_dist.pvalue:
                    is_found = False
                else:
                    is_found = True
                    status = False
                report.update({column: {"p_value": float(is_same_dist.pvalue), "drift_status": is_found}})
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report)
            return status
        
        except Exception as e:  
            raise NetworkSecurityException(e, sys) from e

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            error_message = ""
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            #read data from train and test file path
            train_df = DataValidation.read_data(train_file_path)
            test_df = DataValidation.read_data(test_file_path)

            validation_status = True

            # Validate number of columns
            status = self.validate_number_of_columns(train_df)
            if not status:
                validation_status = False
                error_message += (
                f"Train DataFrame does not have all columns.\n"
                f"Required: {len(self._schema_config['columns'])}, "
                f"Actual: {len(train_df.columns)}\n\n"
            )

            status = self.validate_number_of_columns(test_df)
            if not status:
                validation_status = False
                error_message += (
                f"Test DataFrame does not have all columns.\n"
                f"Required: {len(self._schema_config['columns'])}, "
                f"Actual: {len(test_df.columns)}\n\n"
            )


            ## Check numerical columns 
            status = self.check_numerical_columns_exist(train_df)
            if not status:
                validation_status = False
                error_message += (
                    f"Train DataFrame does not have all numerical columns.\n"
                    f"Required: {self._schema_config['numerical_columns']}, "
                    f"Actual: {list(train_df.columns)}\n\n"
                )
            
            status = self.check_numerical_columns_exist(test_df)
            if not status:
                validation_status = False
                error_message += (
                    f"Test DataFrame does not have all numerical columns.\n"
                    f"Required: {self._schema_config['numerical_columns']}, "
                    f"Actual: {list(test_df.columns)}\n\n"
                )


             ## Check Data Drift
            drift_status = self.detect_dataset_drift(base_df=train_df, current_df=test_df)

            if not drift_status:
                validation_status = False
                error_message += "Data drift detected between train and test datasets.\n\n"
            
            
            if validation_status:
                logging.info("Data validation completed successfully. No issues found.")

                valid_dir = os.path.dirname(self.data_validation_config.valid_train_file_path)
                os.makedirs(valid_dir, exist_ok=True)

                train_df.to_csv(self.data_validation_config.valid_train_file_path, index=False, header=True)
                test_df.to_csv(self.data_validation_config.valid_test_file_path, index=False, header=True)

                logging.info("Validation Successful")

                return DataValidationArtifact(
                    validation_status=validation_status,
                    valid_train_file_path=self.data_validation_config.valid_train_file_path,
                    valid_test_file_path=self.data_validation_config.valid_test_file_path,
                    invalid_train_file_path=None,
                    invalid_test_file_path=None,
                    drift_report_file_path=self.data_validation_config.drift_report_file_path
                )
            else:
                logging.warning("Data validation failed. Issues found during validation.")
                logging.warning(error_message)
                invalid_dir = self.data_validation_config.invalid_data_dir
                os.makedirs(invalid_dir, exist_ok=True)

                invalid_train_file_path = os.path.join(invalid_dir, "invalid_train.csv")
                invalid_test_file_path = os.path.join(invalid_dir, "invalid_test.csv")

                train_df.to_csv(invalid_train_file_path, index=False, header=True)
                test_df.to_csv(invalid_test_file_path, index=False, header=True)

                logging.info("Validation Failed. Invalid data saved.")
                return DataValidationArtifact(
                    validation_status=validation_status,
                    valid_train_file_path=None,
                    valid_test_file_path=None,
                    invalid_train_file_path=invalid_train_file_path,
                    invalid_test_file_path=invalid_test_file_path,
                    drift_report_file_path=self.data_validation_config.drift_report_file_path
                )
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e