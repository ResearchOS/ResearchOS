# Process

## Introduction
This is a [runnable](../Pipeline%20Objects/runnables.md) [Pipeline Object](../Pipeline%20Objects/pipeline_object.md) that is used to process data. This object is used to perform any data processing that is needed before the data can be plotted or summarized.

## Import Attributes
One special case for `Process` objects is when first importing data from their native file formats into ResearchOS. To do that, a couple of custom attributes need to be defined for the `Process` object that performs this task.

The code to be run to import the data from the native file format should be defined in the `method` (Python) or `mfunc_name` (MATLAB) of the `Process` object. The code should handle loading only one file format at a time. If multiple file formats need to be imported, multiple `Process` objects should be created with separate functions for each.

### import_file_ext
A string that specifies the file extension of the native file format. For example, if the native file format is a CSV file, the `import_file_ext` attribute should be set to `csv`.

### import_file_vr_name
A string that specifies the name of the variable that will provide the file path of the file to import the data from. With the [Dataset](../Data%20Objects/dataset.md) `schema` (or `file_schema`) and the `Process` object's `import_file_ext` and `import_file_vr_name` attributes, the full file name of the native data file can be constructed and passed as an input argument to the `Process` object's code.

::: src.ResearchOS.PipelineObjects.process.Process