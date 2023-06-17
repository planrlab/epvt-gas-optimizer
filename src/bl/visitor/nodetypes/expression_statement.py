'''
Created on Nov 30, 2020

@author: ACER
'''
from . import Node, get_logger

from src.bl.visitor import nodetypes as ntypes

class ExpressionStatement(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = True):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+ str(self.get_ast_id()))
        self.set_cfg_id()
        self.__imf_repr = None
        children = node_info.get('children')
        if len(children)>1:
            raise Exception("Error in the Expression Statement")
            
        else:
            child = children[0]
            child_node = getattr(ntypes, child.get('name'))(child, self.get_cfg_id(), False)
            self.used.extend(child_node.used)
            self.dec_def.extend(child_node.dec_def)
            
            self.__imf_repr = child_node.get_imf()
        self.construct_cfg_node(_is_cfg_node)
        
    
    def get_imf(self):
        return self.__imf_repr
    
    def __str__(self):
        return "\n imf: " + str(self.get_imf()) + \
            "\n used: " + str(self.used) + \
            "\n defined: " + str(self.dec_def) + \
            "\n source code:" + self.get_source_code()
        