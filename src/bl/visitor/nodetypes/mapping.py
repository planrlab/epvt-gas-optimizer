'''
Created on Nov 30, 2020

@author: ACER
'''

from . import Node, get_logger
from src.bl.visitor import nodetypes as ntypes


class Mapping(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self._from = None
        self._to = None
        
        children = node_info.get('children')
        
        child = children.pop(0)
        child_node = getattr(ntypes, child.get('name'))(child, _previous, False)
        self._from = child_node.get_type()
        
        child = children.pop(0)
        child_node = getattr(ntypes, child.get('name'))(child, _previous, False)
        self._to = child_node.get_type()
        
        
    def __ETS_node_info(self, info):
        self.set_argument_types(info.get('argumentTypes'))
        self.set_is_constant(info.get('isConstant'))
        self.set_is_lvalue(info.get('isLValue'))
        self.set_is_pure(info.get('isPure'))
        self.set_lvalue_requested(info.get('lValueRequested'))
        self.set_member_name(info.get('member_name'))
        self.set_referenced_declaration(info.get('referencedDeclaration'))
        self.set_type(info.get('type'))
        