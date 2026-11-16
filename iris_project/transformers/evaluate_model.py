import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def evaluate(df, *args, **kwargs):
    y_true = df['target']
    y_pred = df['predicted']

    print('Confusion matrix:')
    print(pd.crosstab(y_true, y_pred, rownames=['actual'], colnames=['predicted']))

    metrics = pd.DataFrame({
        'metric': ['accuracy', 'precision', 'recall', 'f1_score'],
        'value': [
            round(accuracy_score(y_true, y_pred), 3),
            round(precision_score(y_true, y_pred, average='macro'), 3),
            round(recall_score(y_true, y_pred, average='macro'), 3),
            round(f1_score(y_true, y_pred, average='macro'), 3),
        ]
    })
    print(metrics)
    return metrics


@test
def test_metrics(output, *args):
    assert len(output) == 4, 'metrics table must have 4 rows'
    assert output['value'].between(0, 1).all(), 'metrics must be between 0 and 1'
