'''
Created on Nov 30, 2020

@author: ACER
'''
from . import Node, get_logger
from src.bl.visitor import nodetypes as ntypes


class ContractDefinition(Node):
    
    def __init__(self, node_info, _previous = None, _is_cfg_node = False):
        super(self.__class__, self).__init__(node_info, _previous)
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info('processing '+self.__class__.__name__+ str(self.get_ast_id()))
        
        self.__base_contracts = None
        self.__contract_dependencies  = None
        self.__contract_kind = None
        self.__documentation = None
        self.__fully_implemented = None
        self.__linearized_base_contracts = None
        self.__contract_name = None
        self.__scope = None
        
        self.__ETS_node_info(node_info.get('attributes'))
        
        
        '''User scope'''
        self.set_user_scope(self.get_scope())
        
        '''DERIVED Information'''
        self.__functions = []
        
                
        self.set_cfg_id("Contract")
        self.set_name(self.__contract_name)
        
        self.entry_node = Node("start_"+ self.__contract_name)
        self.exit_node = Node("stop_"+ self.__contract_name)
        
        
        '''CFG'''
        current_cfg_node = self.construct_cfg_node(None) #Starting Point
        self.entry_node.construct_cfg_node(None)
        self.exit_node.construct_cfg_node(None)
        
        self.set_next_node(self.entry_node, current_cfg_node)
        
        current_node = self.entry_node
        
        childrens = node_info.get('children')

        for child in childrens:
            isFunction = False    
            if (child.get('name') in ["InheritanceSpecifier"]):
                continue;
            if child.get('name') == 'FunctionDefinition':
                isFunction = True
            
            child_node = getattr(ntypes, child.get('name'))(child, self.get_cfg_id(), current_cfg_node)
            
            if isFunction:
                self.__functions.append(child_node)
                
            
            entry, exit = child_node.get_entry_exit_nodes()
            current_node.set_next_node(entry, current_cfg_node)
            exit.set_next_node(self.exit_node, current_cfg_node)
            self.logger.info(str(child_node.get_imf()))
        
        if _is_cfg_node:
            _is_cfg_node.subgraph(current_cfg_node)
    
    
    def get_functions(self):
        return self.__functions
    
    def get_base_contracts(self):
        return self.__base_contracts
    
    def get_contract_dependencies(self):
        return self.__contract_dependencies
    
    def get_contract_kind(self):
        return self.__contract_kind
    
    def get_documentation(self):
        return self.__documentation

    def get_fully_implemented(self):
        return self.__fully_implemented

    def get_linearized_base_contracts(self):
        return self.__linearized_base_contracts

    def get_contract_name(self):
        return self.__contract_name

    def get_scope(self):
        return self.__scope

    def set_base_contracts(self, value):
        self.__base_contracts = value

    def set_contract_dependencies(self, value):
        self.__contract_dependencies = value

    def set_contract_kind(self, value):
        self.__contract_kind = value

    def set_documentation(self, value):
        self.__documentation = value
        
    def set_fully_implemented(self, value):
        self.__fully_implemented = value
    
    def set_linearized_base_contracts(self, value):
        self.__linearized_base_contracts = value

    def set_contract_name(self, value):
        self.__contract_name = value

    def set_scope(self, value):
        self.__scope = value

    def __ETS_node_info(self, info):
        self.set_contract_name(info.get('name'))
        self.set_base_contracts(info.get('baseContracts'))
        self.set_contract_dependencies(info.get('contractDependencies'))
        self.set_contract_kind(info.get('contractKind'))
        self.set_scope(info.get('scope'))
        self.set_documentation(info.get('documentation'))
        self.set_fully_implemented(info.get('fullyImplemented'))
        self.set_linearized_base_contracts(info.get('linearizedBaseContracts'))
        
    