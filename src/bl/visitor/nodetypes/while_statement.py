'''
Created on Nov 30, 2020

@author: ACER
'''
from . import Node, get_logger
from src.bl.visitor import nodetypes as ntypes

class WhileStatement(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = True):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+str(self.get_ast_id()))
        
        self.entry_node = None
        self.condition = True
        self.loop_statements = None
        
        self.set_cfg_id("While")
        self.set_name("While")
        
        '''CFG'''
        current_cfg_node = self.construct_cfg_node(None) #Starting Point
        
        self.report_control_structure(self)
        
        children = node_info.get("children")     
            
        self.loop_cn = Node("CN_W")
        self.exit_node = Node("JN_W", jn_id=self.loop_cn.get_join_node_id())
        self.loop_cn.set_name("cnt")
        self.exit_node.set_name("brk")
        
        self.loop_cn.construct_cfg_node(None)
        self.exit_node.construct_cfg_node(None)
        
        self.entry_node = self.loop_cn
        
        condition_node = children.pop(0)
        self.condition = getattr(ntypes, condition_node.get('name'))(condition_node, "L_C", current_cfg_node) 
        self.update_used_dec_def(self.condition)
        
        self.entry_node.set_next_node(self.condition, current_cfg_node)
        statements_info = children.pop(0)
        self.loop_statements = getattr(ntypes, statements_info.get('name'))(statements_info, "L_B", current_cfg_node)
        self.update_used_dec_def(self.loop_statements)
        
        entry_node, exit_node = self.loop_statements.get_entry_exit_nodes() 
        if entry_node:
            self.condition.set_next_node(entry_node, current_cfg_node)
            if exit_node:
                exit_node.set_next_node(self.loop_cn, current_cfg_node)
        else:
            self.condition.set_next_node(self.loop_cn, current_cfg_node)
        self.condition.set_next_node(self.exit_node, current_cfg_node)
        self.loop_cn.set_used_dec_def(self)
        self.loop_cn.set_opposite_node(self.exit_node)
        self.loop_cn.report_value_numbering(self.loop_cn.dec_def)
        self.exit_node.report_value_numbering(self.exit_node.dec_def)
        self.loop_cn.report_dym_value_numbering(self.loop_cn.dec_def)
        self.exit_node.local_declarations = self.loop_statements.local_declarations
        self.loop_cn.local_declarations = self.loop_statements.local_declarations        
        self.draw_edges_from_BCR(current_cfg_node, self.loop_cn)
        self.draw_edges_from_BCR(current_cfg_node, self.exit_node)
        assert(self.extract_control_structure() == self)
        if _is_cfg_node:
            _is_cfg_node.subgraph(current_cfg_node)
        
    
    def get_imf(self):
        return None, self.get_name()