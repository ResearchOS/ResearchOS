# Subset

## Introduction
This [Pipeline Object](../Pipeline%20Objects/pipeline_object.md) is used to specify a subset of data to operate on for any [runnable](../Pipeline%20Objects/runnables.md) [Pipeline Object](../Pipeline%20Objects/pipeline_object.md).

## Conditions
`Subset` objects have a `conditions` attribute that is used to specify the criteria to select a subset of data.The `conditions` attribute is a list of dictionaries, where each dictionary can also contain sub-dictionaries. The keys of the dictionaries are either `"and"` or `"or"`. `"and"` is used to specify that all conditions in the sub-dictionary must be met, while `"or"` is used to specify that at least one condition in the sub-dictionary must be met. The values of the dictionaries are lists. Each element of the list is either a sub-dictionary, or a tuple of three elements: the [Variable](../variable.md) object, the logical operator, and the value to compare the variable to. The operators that can be used are `"=="`, `"!="`, `"<"`, `"<="`, `">"`, `">="`, `"in"`, and `"not in"`. The value can be any hard-coded value that can be JSON-serialized using `json.dumps()`.

Here is an example `Subset` object `condition` attribute. This example selects `"Subject1"` and `"Trial1"` where the `vr.value` is greater than 5 or less than 0:
```python
conditions = [
    {
        "and": [
            (vr.subject_name, "==", "Subject1"),
            (vr.trial_name, "==", "Trial1"),
            {
                "or": [
                    (vr.value, ">", 5),
                    (vr.value, "<", 0)
                ]
            }
        ]
    }
]
```

::: src.ResearchOS.PipelineObjects.subset.Subset