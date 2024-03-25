from typing import TYPE_CHECKING
import os

if TYPE_CHECKING:
    from ResearchOS.PipelineObjects.plot import Plot

from ResearchOS.code_runner import CodeRunner

class PlotRunner(CodeRunner):

    def __init__(self) -> None:
        pass

    def compute_and_assign_outputs(self, vr_values_in: dict, pl: "Plot", info: dict = {}, is_batch: bool = False) -> None:
        """Assign the output variables to the DataObject node.
        """

        # 1. Get the plot wrapper function.
        if pl.is_matlab:
            if not self.matlab_loaded:
                raise ValueError("MATLAB is not loaded.")            
            fcn = getattr(self.matlab_eng, "PlotWrapper")
        else:
            fcn = getattr(pl, pl.method)

        # 2. Convert the vr_values_in to the right format.
        if not is_batch:
            vr_vals_in = list(vr_values_in.values())
            vr_vals_in.append(info) # Always include the info variable.
        else:
            # Convert the vr_values_in to the right format.
            vr_vals_in = []
            for vr_name in vr_values_in:
                vr_vals_in.append(vr_values_in[vr_name])

        # 3. Call the plot wrapper function.
        # Provide it with:
        # - the input variables
        # - the plot function name
        # - the file path to save the plot to
        lineage = self.get_node_lineage(self.node, self.dataset_object_graph)
        lineage.remove(self.dataset)
        lineage.remove(self.node)
        dataset_parent_folder = os.path.dirname(self.dataset.dataset_path)
        plots_folder = os.path.join(dataset_parent_folder, "plots")
        save_path = os.path.join(plots_folder, pl.id + " " + pl.name)
        for l in lineage[::-1]:
            save_path = os.path.join(save_path, l.id)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        save_path = os.path.join(save_path, self.node.id)
        try:
            fig_handle = fcn(pl.mfunc_name, save_path, vr_vals_in)
        except PlotRunner.matlab.engine.MatlabExecutionError as e:
            if "ResearchOS:" not in e.args[0]:
                print("'ResearchOS:' not found in error message, ending run.")
                raise e
            return # Do not assign anything, because nothing was done!
        
        # if not isinstance(fig_handle, tuple):
        #     fig_handle = (fig_handle,)

        