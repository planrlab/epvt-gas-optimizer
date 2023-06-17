'''
Created on Dec 2, 2021

@author: ACER
'''
import os

from graphviz import Digraph

os.environ["PATH"] += os.pathsep + 'A:/pot/release/bin/'
    
class CFGDigraph(Digraph):
    join_node = 1
    cid = 1
       
    def __init__(self, previous, file_name = None, edge = True, info = ""):
        super(self.__class__, self).__init__("cluster_"+str(self.__class__.cid), file_name) 
        self.__previous = previous
        self.__class__.cid += 1


    def get_previous(self):
        return self.__previous

    def add_join_node(self, info = None):
        _style = 'filled, dashed'
        _shape = "circle"
        _color = "black"
        if not info:
            _fill_color = ".7 .3 1.0"
        elif info in ["DWL_C","L_C","If_C"]:
            _fill_color = "#ffff66"
            _shape = 'doublecircle'
            _style = 'filled'
        else:
            _fill_color = "darkgoldenrod"
            _style = 'filled' 
        self.node(style = _style, name = info, label=info, fixedsize = 'true', shape = _shape, width='0.7',fillcolor = _fill_color, color = _color, fontsize='10')
    
    
    def add_node(self, name, _label, loop_node = None, _shape = "rectangle", _style = "filled"):
        if loop_node in ["L_C","DWL_C","If_C"]:
            _shape = 'diamond'
            self.node(name, label = _label, style = _style, fillcolor = '#ffff66', color = 'orange', shape = _shape)
        else:
            self.node(name, label = _label, shape = _shape, style = _style)

        
    def join___nodes(self, prevs, curr, _label = None, _color = "black", _font_color = 'black', _labelfontcolor = "black", _style = "filled"): #):
        if not curr in ["break", "continue"]:
            if prevs and curr:
                if type(prevs) is list:
                    for prev in prevs:
                        self.add_edge(prev, curr, _label, _color, _labelfontcolor, _style)                
                else:
                    if prevs.get_n_type() in ["DWL_C","L_C","If_C"] and _color == "black":
                        _color = "red"
                        _label = "F"
                    self.add_edge(prevs, curr, _label, _color, _labelfontcolor, _style)
            else:
                if not curr:
                    pass
        elif prevs:
            if curr == "break":
                self.add_break_link((prevs,""))
            else:
                self.add_continue_link((prevs,""))
                     
                
    def add_edge(self, prev_n, next_n, _label = None, _color = "black", _labelfontcolor = "black", _style = "filled"): 
        if _label == "T":
            _color = "darkgreen"
            _label = "T"
        elif _label == "F":
            _color = "red"
            _label = "F"
        self.edge(prev_n, next_n, label = _label, fillcolor = _color, color = _color, fontcolor =  _labelfontcolor, fontname = "Courier bold", penwidth="1.75", style = _style, overlap = "false", splines = "true")
    
           
class CFGBuilder():
    #__nodes = dict()
    #__modifiers = dict()
    __functions = dict()
    __unreachable_nodes = list()
    __curr_function = None
    __dead_nodes = list()
    
    def __init__(self, shape):
        self.__count = 0
        self.__shape = "box" if shape else "oval"
        self.__file_name = "Fig: Control Flow Diagram"
        self.__mdgraph = CFGDigraph(None, self.__file_name, self.__shape)
        self.__mdgraph.attr(label = self.__file_name.upper(), fontsize = '18')
        self.__curr_dgraph = self.__mdgraph
        
    
    def reset(self):
        CFGDigraph.join_node = 1
        CFGDigraph.cid = 1
        CFGBuilder.__functions = dict()
        CFGBuilder.__unreachable_nodes = []
        CFGBuilder.__curr_function = None
        
       
    def plot(self, cfg_id, src_id, curr_cfg = None):
        node = None
        if curr_cfg:
            self.__curr_dgraph = curr_cfg
            
        if type(cfg_id) is str:
            self.__add_join_node(cfg_id)
        else:        
            #print("C", cfg_id, src_id)
            node_label, name = cfg_id
            #print("Parent block Info::", name)
            if type(node_label) is int:
                self.__create_node(node_label, src_id, name) 
            
            elif node_label == "Source Code":
                node = self.__create_container() 
                
            elif node_label in ["Contract"]:
                node = self.__create_contract(name)
                
            elif node_label in ["Function"]:
                node = self.__create_function(name) 
            
            elif node_label in ["IF"]:
                node = self.__create_if_statement(name)
            
            elif node_label in ["Block"]:
                node = self.__create_block(name)
            
            elif node_label in ["For", "While", "DoWhile"]:
                node = self.__create_for_loop(name)
                
            else:
                node_ltype = node_label[:node_label.find("_")]
                types = ["start", "stop", "START", "STOP"]
                if node_ltype in types:
                    self.__create_entry_exit(node_label, types.index(node_ltype))
                else:
                    #exit continue nodes for loops
                    self.__add_join_node(node_label)
                    
        return node
    
        
    def __add_join_node(self, info):
        self.__curr_dgraph.add_join_node(info)
        
        
    def __loop_conditions(self):
        if not self.__curr_dgraph.get_entry_node():
            #input("Not entry Node")
            j_node = self.__curr_dgraph.get_continue_node()
            #self.__curr_dgraph.set_continue_node(j_node)
            self.__curr_dgraph.set_entry_node(j_node)
            self.__curr_dgraph.set_previous_nodes(j_node)
            return True
        return False
    
    
    
    def __create_node(self, cfg_node_label, src_id = None, ntype = None):
        #self.__count += 1
        """ In case of detailed Information separate class"""
        self.__curr_dgraph.add_node(str(cfg_node_label), src_id, ntype)


    def __create_container(self):
        return CFGDigraph(None)
            
    def __create_block(self, parent_block):
        b = CFGDigraph(self.__curr_dgraph, info = parent_block)
        if parent_block == "Function":
            _color = "black"
            b_color= "#f5f5ef"##e6f3ff"
            
        elif parent_block in ["If_T", "If_TO"]:
            _color = "black"
            b_color = "#bbff99"#ddff99"#71da71"#e6f3ff"
            
        elif parent_block in ["L_B"]:
            _color = "red"
            b_color = "#ffcccc"#ffc2b3"##ffcccc"
        else:    
            _color = "black"
            b_color = "#ffd699"#ffb3b3"#ffe6e6"#ff8566"
            
        b.attr(style='filled', fillcolor=b_color, label='', fontname='Courier bold', fontcolor='darkslategray', fontsize = '16')
        b.node_attr.update(style='filled', fillcolor='snow1', color = _color, shape = self.__shape, fontname='Courier bold', fontcolor='black', fontsize = '12')
        self.__curr_dgraph = b
        return b
    
                
    def __create_if_statement(self, name):
        i = CFGDigraph(self.__curr_dgraph, info = name)
        i.attr(style='filled', fillcolor='snow3', color = "snow2", label='', fontname='Courier bold', fontcolor='darkslategray', fontsize = '16')
        i.node_attr.update(style='filled', fillcolor='#ffff66',shape = "diamond", fontname='Courier bold', fontcolor='black', fontsize = '12')
        self.__curr_dgraph = i
        return i
    
    
    def __create_contract(self, name):
        c = CFGDigraph(self.__curr_dgraph, edge=False, info = name)
        c.attr(style='filled', fillcolor='snow1',color = "snow2", label='Contract::'+name, fontname='Courier bold', fontcolor='#1a0000', fontsize = '16')
        c.node_attr.update(style='filled', fillcolor='#ccccff', shape = self.__shape, fontname='Courier bold', fontcolor='black', fontsize = '14')
        self.__curr_dgraph = c
        self.__curr_function = None
        return c
    
    def __create_entry_exit(self, name, type_id):
        ee = self.__curr_dgraph
        if type_id == 0:
            ee.add_node(name, 'Contract Address', _shape='Mdiamond')
        elif type_id == 1:
            ee.add_node(name, 'End', _shape='Msquare')
        elif type_id == 2:
            ee.add_node(name, 'start', _shape='Mdiamond')
        elif type_id == 3:
            ee.add_node(name, 'stop', _shape='Msquare')
        else:
            #CN_F, JN_F, 
            pass
            ee.__add_join_node(name)
            
            
            
    def __create_function(self, name):
        f = CFGDigraph(self.__curr_dgraph, edge=False, info = "Function::"+name)
        _label = 'Function::'+name
        _style = 'filled'        
        if name.strip() == "":
            _label = 'Constructor'
            _style = 'filled,dashed'
            
        f.attr(style=_style, fillcolor='#e6e6ff', color = "snow2", label=_label, fontname='Courier bold italic', fontcolor='#00004d', fontsize = '14')
        f.node_attr.update(style='filled', fillcolor='white',color ="black", shape = self.__shape, fontname='Courier bold italic', fontcolor='black', fontsize = '12')
        self.__curr_dgraph = f
        return f
    
    def __create_for_loop(self, name):
        fl = CFGDigraph(self.__curr_dgraph, info = name)
        fl.for_init = False
        fl.for_condition = False
        fl.attr(style='filled', fillcolor="#ffe6e6", color = "snow2", fontname='Courier bold', fontcolor='darkviolet', fontsize = '12')
        fl.node_attr.update(style='filled', fillcolor='white', color = 'darkgreen',shape = self.__shape, fontcolor='black', fontsize = '12')
        self.__curr_dgraph = fl
        return fl
    
    
    def draw_cfg(self, dgraph = None, src = True, path = None, cfg_format = 'png', file_name = "cfg"):
        if src:
            file_name += '_src'
        dgraph.render(file_name, path, False, False, cfg_format)
        

                         
    def append_to_cfg(self, dgraph):
        self.__curr_dgraph.subgraph(dgraph)
        