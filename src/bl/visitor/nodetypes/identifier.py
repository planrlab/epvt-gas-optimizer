'''
Created on Nov 30, 2020

@author: ACER
'''


from . import Node
from src.bl.visitor import nodetypes as ntypes
from src.bl.visitor.nodetypes.source_unit import SourceUnit

class Identifier(Node):
    
    def __init__(self, node_info, _previous = None, is_cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.overloaded_declarations = None
        self.referenced_declaration = None
        self.type = None
        self.value = None
        
        if is_cfg_node:
            self.set_cfg_id()
            
        self.__ETS_node_info(node_info.get('attributes'))
        
        self.used.append(self.referenced_declaration)
        
        childrens = node_info.get('children')
        if childrens:
            for child in childrens:
                child_node = getattr(ntypes, child.get('name'))(child, self.get_cfg_id())
        
        if self.get_user_scope() and self.get_referenced_declaration()> self.get_user_scope():
            SourceUnit.insert_operands_info(str(self.referenced_declaration), self)        
        else:
            if self.type.startswith("type(contract"):
                self.referenced_declaration = self.get_ast_id()
                SourceUnit.insert_operands_info(str(self.referenced_declaration), self)
        
        if is_cfg_node:
            self.construct_cfg_node(is_cfg_node)          
                  
                  
    def get_imf(self):
        return self.referenced_declaration
    
    
    def __ETS_node_info(self, info):
        self.set_overloaded_declarations(info.get('overloadedDeclaration'))
        self.set_referenced_declaration(info.get('referencedDeclaration'))
        self.set_type(info.get('type'))
        self.set_value(info.get('value'))
        
                
    def get_overloaded_declarations(self):
        return self.overloaded_declarations


    def get_referenced_declaration(self):
        return self.referenced_declaration


    def get_type(self):
        return self.type


    def get_value(self):
        return self.value


    def set_overloaded_declarations(self, value):
        self.overloaded_declarations = value


    def set_referenced_declaration(self, value):
        self.referenced_declaration = value


    def set_type(self, value):
        self.type = value


    def set_value(self, value):
        self.value = value



