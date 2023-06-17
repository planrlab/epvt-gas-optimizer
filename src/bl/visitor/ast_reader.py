'''
Created on Jul 26, 2019
@author: JH-ANIC
'''
from src.bl.visitor.node_processor import Node
import src.bl.visitor.nodetypes as node_types

class ASTToCFGObject(object):
    
    def __init__(self, source_code, ast_data, _src_label=False):
        Node.reset(source_code , _src_label)
        self.__source_code = source_code
        self.__cfg_object = getattr(node_types, ast_data['name'])(ast_data, None)
        self.__set_reachability(self.__cfg_object)
        self.__cfg_builder = Node.get_cfg_builder()
        Node.get_cfg_builder().draw_cfg(self.__cfg_object.get_dgraph(), path="cfg", cfg_format="png", file_name="cfg")
        
    def __set_reachability(self, ogr):
        pending = [ogr.get_contracts()[0]]
        counter = 0
        while(len(pending) > 0):
            counter += 1
            node = pending.pop()
            if node and node.get_is_unreachable():
                node.set_reachable()
                next_nodes = node.get_next_nodes()
                if isinstance(next_nodes, list):
                    for t_node in next_nodes:
                        pending.append(t_node)
                else:
                    pending.append(next_nodes)

    def get_cfg_object(self):
        return self.__cfg_object
    
    def get_cfg_builder(self):
        return self.__cfg_builder

