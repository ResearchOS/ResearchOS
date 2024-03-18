# Process
Process imports a data type unique to ResearchOS called an **Action**.
An **Action** is a set of sequal queries that perform multiple action with one **Action** object call 

::: src.ResearchOS.PipelineObjects.process.Process

To run a Process with process.run():
1. Create a new Process object, with id specified as a kwarg.
2. Set the level of the Process object as a DataObject subclass.
3. If a MATLAB function is to be run, set self.is_matlab to True.
4. Set the input and output variables.
    a. Use self.set_input_var() and self.set_output_var() to set the input and output variables using kwargs.
    b. Alternatively, assign self.input_vrs and self.output_vrs directly as dicts with keys for the variable names in code, and the Variable objects are the values.
    NOTE: Ensure that all of the variables are pre-existing, and that their vr.name are unique from all other variables in the pipeline.