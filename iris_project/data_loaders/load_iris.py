import pandas as pd
from sklearn.datasets import load_iris

# Import Mage's decorators only if they aren't already loaded
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data(*args, **kwargs):
    iris = load_iris(as_frame=True)
    df = iris.frame                      # 4 feature columns + 'target'
    print('Rows loaded:', len(df))
    return df


@test
def test_output(output, *args):
    assert len(output) == 150, 'Iris must have 150 rows'
