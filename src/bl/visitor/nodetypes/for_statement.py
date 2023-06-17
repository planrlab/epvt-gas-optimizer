'''
Created on Jan 5, 2020

@author: ACER
'''


from . import Node, get_logger
from src.bl.visitor import nodetypes as ntypes
from copy import deepcopy
class ForStatement(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = True):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+str(self.get_ast_id()))
        self.initialization_expression = True
        self.condition = True
        self.loop_expression = True
        self.loop_statements = None
        
        self.set_cfg_id("For")
        self.set_name("For")
        
        '''CFG'''
        current_cfg_node = self.construct_cfg_node(None) #Starting Point
        self.report_control_structure(self)
        
        children = self.__ETS_node_info(node_info)
        
        self.entry_node = None
        self.loop_cn = Node("CN_F")
        self.exit_node = Node("JN_F", jn_id=self.loop_cn.get_join_node_id())
        
        self.loop_cn.set_name("cnt")
        self.exit_node.set_name("brk")
        
        self.loop_cn.construct_cfg_node(None)
        self.exit_node.construct_cfg_node(None)
        
        if self.initialization_expression:
            initialization_expression_info = children.pop(0)
            self.initialization_expression_node = getattr(ntypes, initialization_expression_info.get('name'))(initialization_expression_info, "For_E", current_cfg_node)
            self.entry_node = self.initialization_expression_node
            self.entry_node.set_next_node(self.loop_cn, current_cfg_node)
#             self.insert_g_used(self.entry_node.get_used())
            self.logger.info(str(self.entry_node.get_imf()))
        else:
            self.entry_node = self.loop_cn
       
        current_node = self.loop_cn
        
        if self.condition:
            condition_info = children.pop(0)     
            self.condition = getattr(ntypes, condition_info.get('name'))(condition_info, "L_C", current_cfg_node)
            self.update_used_dec_def(self.condition)
            self.insert_g_used(self.condition.get_used())
            current_node.set_next_node(self.condition, current_cfg_node)
            current_node = self.condition
            self.logger.info(str(current_node.get_imf()))
            current_node.set_next_node(self.exit_node, current_cfg_node)
            
        statements_info = children.pop(0)
        self.loop_statements = getattr(ntypes, statements_info.get('name'))(statements_info, "L_B", current_cfg_node)
        
        self.update_used_dec_def(self.loop_statements)
        entry_node, exit_node = self.loop_statements.get_entry_exit_nodes()
        
        if entry_node:
            current_node.set_next_node(entry_node, current_cfg_node)
            exit_node.set_next_node(self.loop_cn, current_cfg_node)
        else:
            current_node.set_next_node(self.loop_cn, current_cfg_node)
        
        self.loop_cn.set_used_dec_def(self)
        self.loop_cn.set_opposite_node(self.exit_node)
        self.exit_node.set_used_dec_def(self)
        self.loop_cn.report_value_numbering(self.loop_cn.dec_def)
        self.exit_node.report_value_numbering(self.loop_cn.dec_def)
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
    
    
    def __ETS_node_info(self, info):
        attributes = info.get('attributes')
        if attributes:
            self.initialization_expression = attributes.get('initializationExpression', True)
            self.condition = attributes.get('condition', True)
            self.loop_expression = attributes.get('loopExpression', True)
        
        children = info.get("children")
        
        if self.loop_expression:
            block_stmts = children.pop(-1)
            loop_expression = children.pop(-1)
            
            if block_stmts.get('name') != 'Block':
                block_stmts = {'id':block_stmts.get('id')*-1, 'src':block_stmts.get('src'), 'name':'Block', 'children':[deepcopy(block_stmts)]}            
            block_stmts['children'].append(loop_expression)
            children.append(block_stmts)
            
        return children

