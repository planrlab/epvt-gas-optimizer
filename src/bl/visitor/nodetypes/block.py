'''
Created on Nov 30, 2020

@author: ACER
'''
from . import Node, get_logger

from src.bl.visitor import nodetypes as ntypes


class Block(Node):
    
    def __init__(self, node_info, _previous=None, _is_cfg_node=False):
        super(self.__class__, self).__init__(node_info, _previous)
#         self.logger = get_logger(self.__class__.__name__)
#         self.logger.info('processing '+self.__class__.__name__+str(self.get_ast_id()))
        
        self.local_declarations = []
        
        children = node_info.get('children')
        self.set_cfg_id("Block")
        self.set_name(_previous)
        
        '''CFG'''
        self.current_cfg_node = self.construct_cfg_node(None)  # Starting Point
        if not self.current_cfg_node:
            raise Exception("Required new DG here")
        
        self.__ETS_node_info(children)
        
        if _is_cfg_node:
            _is_cfg_node.subgraph(self.current_cfg_node)
    
    def get_dec_def(self):
        for i in self.local_declarations:
            for j in self.dec_def:
                if j == i:
                    self.dec_def.remove(i)
            
    def __ETS_node_info(self, children):        
        self.set_cfg_id("Block")
        self.entry_node = None
        self.exit_node = None
        entry_node, exit_node, temp = None, None, None
        reachable = True
        for child in children:
            child_node = getattr(ntypes, child.get('name'))(child, self.is_in_loop(), self.current_cfg_node)
            entry_node, exit_node = child_node.get_entry_exit_nodes()
            if reachable:
                if child_node.__class__.__name__ == "VariableDeclarationStatement":
                    self.local_declarations.extend(child_node.dec_def)
                if not self.entry_node:
                    self.entry_node = entry_node
                if isinstance(entry_node.get_cfg_id(), int):
                    self.insert_g_used(entry_node.get_used())
            n_name = child_node.get_name()
            if n_name in ["Return", "Break", "Continue"]:                
                if n_name == "Return":
                    return_node = self.get_return_node()
                    if not exit_node:  # Literals Identifiers etc
                        exit_node = entry_node
                    if temp:
                        temp.set_next_node(child_node, self.current_cfg_node)  # 75 at 72
                    exit_node.set_next_node(return_node, self.current_cfg_node, extra=False)
                    if reachable:
                        exit_node.dec_def.extend(self.dec_def)                        
                else:
                    b_node, c_node = self.get_break_continue()          
                    if n_name == "Continue":
                        if temp:
                            temp.set_next_node(c_node, self.current_cfg_node, extra=False)
                            if reachable:
                                c_node.dec_def.extend(self.dec_def)
                    else: 
                        if temp:
                            temp.set_next_node(b_node, self.current_cfg_node, extra=False)
                            if reachable:
                                b_node.dec_def.extend(self.dec_def)
                                b_node.report_dym_value_numbering(self.dec_def)
                self.dec_def = list()
                self.used = list() 
                temp = None
                reachable = False
            else:
                if temp:
                    temp.set_next_node(entry_node, self.current_cfg_node, spec="cnt" if entry_node.get_name() == "cnt" else None)
                temp = exit_node
                        
            if reachable:
                self.update_used_dec_def(child_node)
        self.exit_node = temp
    
    def get_imf(self):
        return "Block", self.get_name()

