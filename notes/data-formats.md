One aspect of loading files that needs to be understood is what data formats are allowed, and how
they can appear to be interpreted correctly.

The data formats slated for initial release:

1. csv
1. JSON

# CSV

CSV files are typically made in the following format:

```csv
column1_name,column2_name,column3_name,...
row1_column1_value, row1_column2_value, row1_column3_value,...
row2_column1_value, row2_column2_value, row2_column3_value,...
...
```

This is easy to automatically interpret. When uploading a file in this format, we will want to read it to understand its data types, columns, and other metadata. Ideally, we can store this information so that later usage of the file can just load the metadata, without needing to recreate it.

Later down the line, we can generate automatic databases of these csv files for easier analysis, and to enable ad-hoc queries.

# JSON

JSON files can contain data of arbitrary structure, so we need to define a structure that will be accepted here. The main use-case for the first release will be to analyze results files from data-processing workloads.

We need to ensure that we allow easy viewing of a single result, as well as an easy way to compare multiple results to find trends or outliers. For this use case we will expect all incoming JSON files to have this format:

```json
{
    "type": supported file types: result,
    "data": [
        {
            "metadata": {
                ...arbitrary key-value pairs...
            },
            "sections": {
                "<section-name>": {
                    ...section data as key-value pairs...
                },
                ...
            },
            "section-order": ["<section-name1>", "<section-name2>", ...]
        },
        {
            ...
        },
        ...
    ]
}
```

The sections will contain the different input or output values. The idea is that across the different results, you can compare values from the same sections. For example, a section might look like this:

```json
{
    ...,
    "results": {
        "correct": 20.11731843575419,
        "test_loss": 0.5443660765886307
    },
    ...
}
```

Or like this:

```json
{
    ...,
    "params": {
        "train_percentage": 0.8,
        "batch_size": 32,
        "epochs": 100,
        "learning_rate": 0.01,
        "model_type": "basic",
        "loss_function": "bce",
        "optimizer": "sgd"
    },
    ...
}
```

This will allow a variety of results to be compared without requiring a fully defined structure which might cause friction to extend.
