from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig, DataValidationConfig, DataTransformationConfig, ModelTrainerConfig
import sys

if __name__ == "__main__":
    try:
        training_pipeline_config = TrainingPipelineConfig()
        dataingestionconfig=DataIngestionConfig(training_pipeline_config=training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config=dataingestionconfig)
        logging.info("Starting data ingestion process")
        data_ingestion_artifact =data_ingestion.initiate_data_ingestion()
        logging.info("Data ingestion process completed successfully")
        print(f"Data Ingestion Artifact: {data_ingestion_artifact}")
        data_validation_config=DataValidationConfig(training_pipeline_config=training_pipeline_config)
        data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact, data_validation_config=data_validation_config)
        logging.info("Starting data validation process")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("Data validation process completed successfully")
        print(f"Data Validation Artifact: {data_validation_artifact}")
        logging.info("Starting data transformation process")
        data_transformation_config = DataTransformationConfig(training_pipeline_config=training_pipeline_config)
        data_transformation = DataTransformation(data_validation_artifact=data_validation_artifact, data_transformation_config=data_transformation_config)
        logging.info("Starting data transformation process")
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        logging.info("Data transformation process completed successfully")
        print(f"Data Transformation Artifact: {data_transformation_artifact}")

        logging.info("Model Training Started")
        model_trainer_config = ModelTrainerConfig(training_pipeline_config)
        model_trainer = ModelTrainer(model_trainer_config=model_trainer_config, data_transformation_artifact=data_transformation_artifact)
        model_trainer_artifact = model_trainer.inititate_model_trainer()
        logging.info("Model Training Artifact created")
        print(f'Data Model Artifact: {model_trainer_artifact}')

    except Exception as e:
        raise NetworkSecurityException(e, sys)


