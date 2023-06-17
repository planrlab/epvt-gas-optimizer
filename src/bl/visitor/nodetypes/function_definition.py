'''
Created on Nov 30, 2020

@author: ACER
'''
from . import Node, get_logger
from src.bl.visitor.nodetypes.source_unit import SourceUnit
from src.bl.visitor import nodetypes as ntypes

class FunctionDefinition(Node):
    
    #For break and continue
    control_loops = []
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
#         print('processing '+self.__class__.__name__+ str(self.get_ast_id()))
        """
        Node Specific Parameters
        """
        self.func_name = None
        self.is_implemented = None
        self.is_constructor = None
        self.kind = None
        self.modifiers = None
        self.scope = None
        self.state_mutability = None
        self.super_function = None
        self.visibility = None
        self.id = None
        
        self.__ETS_node_info(node_info.get('attributes'))
        
        self.set_cfg_id("Function")
        uid = str(self.id)
        self.entry_node = Node("START_"+ self.func_name+uid)
        self.exit_node = Node("STOP_"+ self.func_name+uid)
        self.exit_node.set_name("exit")
        '''CFG'''
        current_cfg_node = self.construct_cfg_node(None) #Starting Point
        self.entry_node.construct_cfg_node(None)
        self.exit_node.construct_cfg_node(None)
        
        Node.reset_function_init(self.exit_node)
        
        current_node = self.entry_node
        
        children = node_info.get('children')
  
        for child in children:
            child_node = getattr(ntypes, child.get('name'))(child, self.get_cfg_id(), current_cfg_node) #(child, self.get_cfg_id(), True)
            if child_node.get_node_type() in ["ModifierInvocation", "OverrideSpecifier"]:
                continue
            t_entry_node, t_exit_node = child_node.get_entry_exit_nodes()
            
            if child_node.get_cfg_id() and t_entry_node: 
                current_node.set_next_node(t_entry_node, current_cfg_node)
                current_node = t_exit_node
        
        if current_node:       
            current_node.set_next_node(self.exit_node, current_cfg_node)
        
        self.draw_edges_from_BCR(current_cfg_node, self.exit_node)
        
        if _is_cfg_node:
            _is_cfg_node.subgraph(current_cfg_node)
        
        SourceUnit.insert_operands_info(str(self.id), self)
    
        
    def get_imf(self):
        return None, self.func_name
    
    
    def get_start_node(self):
        return self.entry_node
    
    
    def __ETS_node_info(self, info):
        self.func_name = info.get('name')
        self.set_name(self.func_name)
        self.set_is_implemented(info.get('implemented'))
        self.set_is_constructor(info.get('constructor'))
        self.set_kind(info.get('kind'))
        self.set_modifiers(info.get('modifiers'))
        self.set_scope(info.get('scope'))
        self.set_state_mutability(info.get('stateMutability'))
        self.set_super_function(info.get('superFunction'))
        self.set_visibility(info.get('visibility'))
        self.id = self.get_ast_id()

    def get_is_implemented(self):
        return self.is_implemented


    def get_is_constructor(self):
        return self.is_constructor


    def get_kind(self):
        return self.kind


    def get_modifiers(self):
        return self.modifiers


    def get_scope(self):
        return self.scope


    def get_state_mutability(self):
        return self.state_mutability


    def get_super_function(self):
        return self.super_function


    def get_visibility(self):
        return self.visibility


    def set_is_implemented(self, value):
        self.is_implemented = value


    def set_is_constructor(self, value):
        self.is_constructor = value


    def set_kind(self, value):
        self.kind = value


    def set_modifiers(self, value):
        self.modifiers = value


    def set_scope(self, value):
        self.scope = value


    def set_state_mutability(self, value):
        self.state_mutability = value


    def set_super_function(self, value):
        self.super_function = value


    def set_visibility(self, value):
        self.visibility = value


    def get_type(self):
        return self.get_kind()
    
    def get_variable_name(self):
        return self.get_name()