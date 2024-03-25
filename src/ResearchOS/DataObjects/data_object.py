"""The base class for all data objects. Data objects are the ones not in the digraph, and represent some form of data storage.""" 
from typing import Any, TYPE_CHECKING
import pickle

if TYPE_CHECKING:    
    from ResearchOS.PipelineObjects.process import Process
    from ResearchOS.variable import Variable

from ResearchOS.research_object import ResearchObject
from ResearchOS.default_attrs import DefaultAttrs
from ResearchOS.action import Action
from ResearchOS.sql.sql_runner import sql_order_result
from ResearchOS.sqlite_pool import SQLiteConnectionPool

all_default_attrs = {}

computer_specific_attr_names = []

class DataObject(ResearchObject):
    """The parent class for all data objects. Data objects represent some form of data storage, and approximately map to statistical factors."""    

    def __delattr__(self, name: str, action: Action = None) -> None:
        """Delete an attribute. If it's a builtin attribute, don't delete it.
        If it's a VR, make sure it's "deleted" from the database."""
        default_attrs = DefaultAttrs(self).default_attrs
        if name in default_attrs:
            raise AttributeError("Cannot delete a builtin attribute.")
        if name not in self.__dict__:
            raise AttributeError("No such attribute.")
        if action is None:
            action = Action(name = "delete_attribute")
        vr_id = self.__dict__[name].id        
        params = (action.id, self.id, vr_id)
        if action is None:
            action = Action(name = "delete_attribute")
        action.add_sql_query(self.id, "vr_to_dobj_insert_inactive", params)
        action.execute()
        del self.__dict__[name]

    def _load_vr_value(self, vr: "Variable", action: Action, process: "Process" = None, vr_name_in_code: str = None, node_lineage: list = []) -> Any:
        """Load the value of a VR from the database for this data object.

        Args:
            vr (Variable): ResearchOS Variable object to load the value of.
            process (Process): ResearchOS Process object that this data object is part of.
            action (Action): The Action that this is part of.

        Returns:
            Any: The value of the VR for this data object.
        """
        func_result = {}
        func_result["input_vrs_names_dict"] = None
        from ResearchOS.variable import Variable
        # 1. Check that the data object & VR are currently associated. If not, throw an error.
        cursor = action.conn.cursor()
        self_idx = node_lineage.index(self)
        for node in node_lineage[self_idx:]:
            if isinstance(vr, Variable):
                sqlquery_raw = "SELECT action_id, is_active FROM vr_dataobjects WHERE dataobject_id = ? AND vr_id = ?"
                sqlquery = sql_order_result(action, sqlquery_raw, ["dataobject_id", "vr_id"], single = True, user = True, computer = False)
                params = (node.id, vr.id)            
                result = cursor.execute(sqlquery, params).fetchall()
                if len(result) > 0:
                    break
            else:
                # TODO: Handle dict of {type: attr_name}
                # If the value is a str, then it's a builtin attribute.
                # Otherwise, if the value is a Variable, then it's a Variable and need to load its value. using self.load_vr_value()
                pass
        if len(result) == 0:
            func_result["do_run"] = False
            func_result["exit_code"] = 1
            func_result["message"] = f"Failed to run {self.name} ({self.id}). {vr_name_in_code} ({vr.id}) not actively connected to {node.id}."
            func_result["vr_values_in"] = None
            return func_result # If that variable does not exist for this dataobject, skip processing this dataobject.
        is_active = result[0][1]
        if is_active == 0:
            raise ValueError(f"The VR {vr.name} is not currently associated with the data object {node.id}.")
        
        # 2. Load the data hash from the database.
        if hasattr(process, "vrs_source_pr"):
            pr = process.vrs_source_pr[vr_name_in_code]
        else:
            pr = process
        if not isinstance(pr, list):
            pr = [pr]
        sqlquery_raw = "SELECT data_blob_hash, pr_id FROM data_values WHERE dataobject_id = ? AND vr_id = ? AND pr_id IN ({})".format(", ".join(["?" for _ in pr]))
        params = (node.id, vr.id) + tuple([pr_elem.id for pr_elem in pr])
        sqlquery = sql_order_result(action, sqlquery_raw, ["dataobject_id", "vr_id"], single = True, user = True, computer = False)        
        result = cursor.execute(sqlquery, params).fetchall()
        if len(result) == 0:
            raise ValueError(f"The VR {vr.name} does not have a value set for the data object {node.id} from Process {process.id}.")
        if len(result) > 1:
            raise ValueError(f"The VR {vr.name} has multiple values set for the data object {node.id} from Process {process.id}.")
        pr_ids = [x[1] for x in result]
        pr_idx = None
        for pr_id in pr_ids:
            pr_idx = None
            try:
                pr_idx = pr_ids.index(pr_id)
            except:
                pass
            if pr_idx is not None:
                break
        if pr_idx is None:
            raise ValueError(f"The VR {vr.name} does not have a value set for the data object {node.id} from any process provided.")
        data_hash = result[pr_idx][0]

        # 3. Get the value from the data_values table. 
        pool_data = SQLiteConnectionPool(name = "data")
        conn_data = pool_data.get_connection()
        cursor_data = conn_data.cursor()
        sqlquery = "SELECT data_blob FROM data_values_blob WHERE data_blob_hash = ?"        
        params = (data_hash,)
        value = cursor_data.execute(sqlquery, params).fetchone()[0]
        pool_data.return_connection(conn_data)
        func_result["do_run"] = True
        func_result["exit_code"] = 0
        func_result["message"] = f"Success in {self.name} ({self.id}). Lookup VR found: {vr_name_in_code} ({vr.id})"
        func_result["vr_values_in"] = pickle.loads(value)
        return func_result

    # def load_dataobject_vrs(self, action: Action) -> None:
    #     """Load all current data values for this data object from the database."""
    #     # 1. Get all of the latest address_id & vr_id combinations (that have not been overwritten) for the current schema for the current database.
    #     # Get the schema_id.
    #     # TODO: Put the schema_id into the data_values table.
    #     # 1. Get all of the VRs for the current object.
    #     from ResearchOS.variable import Variable

    #     sqlquery_raw = "SELECT vr_id FROM vr_dataobjects WHERE dataobject_id = ? AND is_active = 1"
    #     sqlquery = sql_order_result(action, sqlquery_raw, ["dataobject_id", "vr_id"], single = True, user = True, computer = False)
    #     params = (self.id,)        
    #     cursor = action.conn.cursor()
    #     vr_ids = cursor.execute(sqlquery, params).fetchall()        
    #     vr_ids = [x[0] for x in vr_ids]
    #     for vr_id in vr_ids:
    #         vr = Variable(id = vr_id)
    #         self.__dict__[vr.name] = vr