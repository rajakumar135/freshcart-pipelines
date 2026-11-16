if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


# Own block (C4): sits between load_iris and prepare_data.
# It stops the pipeline early if the data is not what the model expects.
@transformer
def validate(df, *args, **kwargs):
    print('Missing values:', int(df.isna().sum().sum()),
          '| classes:', sorted(df['target'].unique().tolist()))
    return df


@test
def test_no_missing_and_three_classes(output, *args):
    assert output.isna().sum().sum() == 0, 'Iris data has missing values'
    assert output['target'].nunique() == 3, 'Expected exactly 3 classes'
