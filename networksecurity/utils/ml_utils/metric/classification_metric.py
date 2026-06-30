from networksecurity.entity.artifact_entity import ClassificationMetricArtifact
from sklearn.metrics import f1_score, precision_score, recall_score
from networksecurity.exception.exception import NetworkSecurityException
import sys, os

def get_classification_score(y_true, y_pred) -> ClassificationMetricArtifact:
    try:
        f1 = f1_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        classification_metric = ClassificationMetricArtifact(model_f1_score=f1, model_precision=precision, model_recall=recall)
        return classification_metric
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e