'''
Created on Nov 30, 2020

@author: ACER
'''
from . import Node, get_logger, SourceUnit

from src.bl.visitor import nodetypes as ntypes

class VariableDeclaration(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = True):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+ str(self.get_ast_id()))
        
        self.is_constant = None
        self.variable_name = None
        self.scope = None
        self.is_state_variable = None
        self.storage_location = None
        self.type = None
        self.value = None
        self.visibility = None       
        self.id = None
        self.data_type = None   
        self.type_declaration_only = False
        
        self.__ETS_node_info(node_info.get('attributes'))
        
        
        if self.variable_name == "":
            self.type_declaration_only = True
        else:
            self.dec_def.append(self.id)
              
        if _is_cfg_node:
            self.set_cfg_id()
            self.entry_node = self
            self.exit_node = self
            self.construct_cfg_node(None)
            
            
        children = node_info.get('children')
        for child in children:
            child_node = getattr(ntypes, child.get('name'))(child, self.get_cfg_id(), False)
        self.__generate_data_type()
        SourceUnit.insert_operands_info(str(self.id), self)
    
        
    def set_data_type(self, dt_name):
        self.data_type = dt_name
    
    
    def get_data_type(self):
        return self.data_type
    
    
    def __generate_data_type(self):
        self.data_type =  str(self.get_type()+" "+ self.get_storage_location()) if self.get_storage_location() != "default" else self.get_type()
    
       
    def get_imf(self):
        return self.id
    
      
    def __str__(self):
        return "\n is_constact: " + str(self.is_constant) + \
            "\n variable_name: " + str(self.variable_name) + \
            "\n is_state_variable: " + str(self.is_state_variable) + \
            "\n storage_location: " + str(self.storage_location) + \
            "\n type: " + str(self.type) + \
            "\n value: " + str(self.value) + \
            "\n visibility: " + str(self.visibility) + \
            "\n scope: " + str(self.scope) + \
            "\n imf: " + str(self.get_imf()) + \
            "\n used: " + str(self.used) + \
            "\n defined: " + str(self.dec_def) + \
            "\n source code:" + self.get_source_code() + \
            "\n id: " + str(self.id)
            
            
        
    def __ETS_node_info(self, info):
        self.set_is_constant(info.get('constant'))
        self.set_variable_name(info.get('name'))
        self.set_scope(info.get('scope'))
        self.set_is_state_variable(info.get('stateVariable'))
        self.set_storage_location(info.get('storageLocation'))
        self.set_type(info.get('type'))
        self.set_value(info.get('value'))
        self.set_visibility(info.get('visibility'))
        self.id = self.get_ast_id()

    def get_is_constant(self):
        return self.is_constant


    def get_variable_name(self):
        return self.variable_name


    def get_scope(self):
        return self.scope


    def get_is_state_variable(self):
        return self.is_state_variable


    def get_storage_location(self):
        return self.storage_location


    def get_type(self):
        return self.type


    def get_value(self):
        return self.value


    def get_visibility(self):
        return self.visibility


    def set_is_constant(self, value):
        self.is_constant = value


    def set_variable_name(self, value):
        self.variable_name = value


    def set_scope(self, value):
        self.scope = value


    def set_is_state_variable(self, value):
        self.is_state_variable = value


    def set_storage_location(self, value):
        self.storage_location = value


    def set_type(self, value):
        self.type = value


    def set_value(self, value):
        self.value = value


    def set_visibility(self, value):
        self.visibility = value