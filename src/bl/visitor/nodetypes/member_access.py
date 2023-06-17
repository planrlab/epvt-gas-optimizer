'''
Created on Nov 30, 2020

@author: ACER
'''

from . import Node, get_logger
from src.bl.visitor import nodetypes as ntypes


class MemberAccess(Node):
    
    def __init__(self, node_info, _previous = None, cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+str(self.get_ast_id()))
        
        self.__argument_types = None
        self.__is_constant = False
        self.__is_lvalue = True
        self.__is_pure = False
        self.__lvalue_requested = False
        self.__member_name = None
        self.__referenced_declaration = None
        self.__type  = None
        
        self.__ETS_node_info(node_info.get('attributes'))
        
        self.__imf_repr = []
        
        children = node_info.get('children')
        
        child = children.pop(0)
        child_node = getattr(ntypes, child.get('name'))(child, self, False)
        self.__imf_repr.append(child_node.get_imf())
        self.__imf_repr.append( self.__referenced_declaration if self.__referenced_declaration else self.__member_name)
    
    
    def get_imf(self):
        return tuple(self.__imf_repr)
       
           
    def get_argument_types(self):
        return self.__argument_types


    def get_is_constant(self):
        return self.__is_constant


    def get_is_lvalue(self):
        return self.__is_lvalue


    def get_is_pure(self):
        return self.__is_pure


    def get_lvalue_requested(self):
        return self.__lvalue_requested


    def get_member_name(self):
        return self.__member_name


    def get_referenced_declaration(self):
        return self.__referenced_declaration


    def get_type(self):
        return self.__type


    def set_argument_types(self, value):
        self.__argument_types = value


    def set_is_constant(self, value):
        self.__is_constant = value


    def set_is_lvalue(self, value):
        self.__is_lvalue = value


    def set_is_pure(self, value):
        self.__is_pure = value


    def set_lvalue_requested(self, value):
        self.__lvalue_requested = value


    def set_member_name(self, value):
        self.__member_name = value


    def set_referenced_declaration(self, value):
        self.__referenced_declaration = value


    def set_type(self, value):
        self.__type = value

  
    def __ETS_node_info(self, info):
        self.set_argument_types(info.get('argumentTypes'))
        self.set_is_constant(info.get('isConstant'))
        self.set_is_lvalue(info.get('isLValue'))
        self.set_is_pure(info.get('isPure'))
        self.set_lvalue_requested(info.get('lValueRequested'))
        self.set_member_name(info.get('member_name'))
        self.set_referenced_declaration(info.get('referencedDeclaration'))
        self.set_type(info.get('type'))
    