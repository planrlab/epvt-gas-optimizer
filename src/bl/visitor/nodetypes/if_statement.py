from . import Node, get_logger
from src.bl.visitor import nodetypes as ntypes


class IfStatement(Node):

    def __init__(self, node_info, _previous=None, _is_cfg_node=True):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing ' + self.__class__.__name__ + str(self.get_ast_id()))
        self.local_declarations = []
        self.entry_node = None
        self.condition = None
        self.true_block = True
        self.false_block = True
        self.exit_node = Node("JN_IF")
        
        self.set_cfg_id("IF")
        self.set_name("IF")
        
        '''CFG'''
        self.current_cfg_node = self.construct_cfg_node(None)  # Starting Point
        self.exit_node.construct_cfg_node(None)
        children = node_info.get("children")   
        condition_node = children.pop(0)
        self.condition = getattr(ntypes, condition_node.get('name'))(condition_node, "If_C", self.current_cfg_node)
        self.update_used_dec_def(self.condition)
        self.entry_node = self.condition
        count = len(children)
        self.__ETS_node_info(node_info)
        if self.true_block:
            true_block = children.pop(0)
            self.true_block = getattr(ntypes, true_block.get('name'))(true_block, "If_T" if count > 1 else "If_TO", self.current_cfg_node)
        self.__link_blocks(self.true_block, "T")
        self.update_used_dec_def(self.condition)
        if self.false_block:
            false_block = children.pop(0)
            self.false_block = getattr(ntypes, false_block.get('name'))(false_block, "If_F", self.current_cfg_node)
        self.__link_blocks(self.false_block, "F")
        self.true_block.get_dec_def()
        if self.false_block:
            self.false_block.get_dec_def()        
        self.update_used_dec_def(self.true_block)    
        self.update_used_dec_def(self.false_block)
        self.exit_node.update_used_dec_def(self)
        self.exit_node.local_declarations = self.true_block.local_declarations
        self.exit_node.report_value_numbering(self.exit_node.dec_def)
        self.exit_node.report_dym_value_numbering(self.true_block.dec_def)
        
        if self.false_block:
            self.exit_node.report_dym_value_numbering(self.false_block.dec_def)
            self.exit_node.local_declarations.extend(self.false_block.local_declarations)
    
        self.condition.set_opposite_node(self.exit_node)        
        if _is_cfg_node:
            _is_cfg_node.subgraph(self.current_cfg_node)
    
    def __ETS_node_info(self, info):
        attributes = info.get('attributes')
        if attributes:
            self.false_block = attributes.get('falseBody', True)
            self.true_block = attributes.get('trueBody', True)

    def get_imf(self):
        return "IF", self.get_name()

    def __link_blocks(self, _block, btype):
        if _block:
            entry_node, exit_node = _block.get_entry_exit_nodes()
            self.entry_node.set_next_node(entry_node if entry_node else self.exit_node, self.current_cfg_node, btype)
            if exit_node:
                exit_node.set_next_node(self.exit_node, self.current_cfg_node)
        else:
            self.entry_node.set_next_node(self.exit_node, self.current_cfg_node, btype)
            
