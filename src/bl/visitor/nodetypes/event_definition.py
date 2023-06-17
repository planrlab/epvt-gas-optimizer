'''
Created on Feb 20, 2021

@author: ACER
'''
from . import Node, get_logger

from src.bl.visitor import nodetypes as ntypes
from src.bl.visitor.nodetypes.source_unit import SourceUnit



class EventDefinition(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = True):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+ str(self.get_ast_id()))
        
        self.set_cfg_id()
        
        self.__anonymous = None
        self.__documentation = None
        self.__name  = None
        self.__ETS_node_info(node_info.get('attributes'))
        children = node_info.get('children')
        
        for child in children:
            child_node = getattr(ntypes, child.get('name'))(child, self, False)
        
        SourceUnit.insert_operands_info(self.get_ast_id(), self)
        
    def get_anonymous(self):
        return self.__anonymous


    def get_documentation(self):
        return self.__documentation


    def get_name(self):
        return self.__name


    def set_anonymous(self, value):
        self.__anonymous = value


    def set_documentation(self, value):
        self.__documentation = value


    def set_name(self, value):
        self.__name = value

   
    def __ETS_node_info(self, info):
        self.set_anonymous(info.get("anonymous"))
        self.set_documentation(info.get("documentation"))
        self.set_name(info.get("name"))
        
