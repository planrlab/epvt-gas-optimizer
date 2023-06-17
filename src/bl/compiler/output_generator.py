'''
Created on ६ मे, २०१९

@author: JH-ANIC
'''
import solcx
from copy import deepcopy

class CompiledOutputGenerator(object):
    '''
    classdocs
    '''
    OPTIONS = ['abi', 'bin', 'opcodes', 'asm']
    
    def __init__(self, source_code):
        self.__init_helper(source_code)
        """
        Solidity Compiler Version Need to set and cal
        After Deploy:::: => GET Call Mapping
        """
    
    def __init_helper(self, source_code):
        self.__source_code = source_code
        self.__compiled_result = solcx.compile_source(self.__source_code)
        self.__contracts_list = self.__extract_modify_compiled_output() 
        self.__contract_name = self.__contracts_list[0]
        #print("AST:", self.__compiled_result.get(self.__contract_name)['ast'])
        #self.ast_data[list(self.ast_data.keys())[0]]['ast']
        
        
    def get_ast(self):
        return deepcopy(self.__compiled_result.get(self.__contract_name)['ast'])
    
        
    def set_contract(self, contract_name):
        self.__contract_name = contract_name 
        
        
    def get_source_code(self):
        return self.__source_code


    def get_contracts_list(self):
        return self.__contracts_list


    def get_byte_code(self): 
        return self.__get_option_output(1)
        
        
    def get_opcodes(self):
        return self.__get_option_output(2)


    def get_abi(self):
        return self.__get_option_output(0)


    def get_source_mapping(self):
        return self.__map_to_source()
    

    def reinitialize_helper(self, source_code):
        self.__init_helper(source_code)
    
    
    def __is_contract_available(self):
        return self.__contract_name in self.get_contracts_list()
    
    
    def __extract_modify_compiled_output(self):
        compiled_output = dict()
        contracts = []
        for contract in self.__compiled_result.keys():
            contract_name = contract.split(":")[1]
            contracts.append(contract_name)
            compiled_output[contract_name] = self.__compiled_result.get(contract)
        self.__compiled_result = compiled_output # Modified as per the contracts name
        return tuple(contracts)
    
    
    def __get_option_output(self, option):
        if self.__is_contract_available(): 
            return self.__compiled_result.get(self.__contract_name)[self.OPTIONS[option]]
        else:
            raise Exception("Invalid Contract Name")
        
        
    def __extract_code_info(self, obj):
        code_info = []       
        for key in obj:
            if key == ".code":
                code_info.extend(obj[key]) 
            elif type(obj[key]) is dict:
                code_info.extend(self.__extract_code_info(obj[key]))
        return code_info
    
    
    def __map_to_source(self):
        code_info_list = self.__extract_code_info(self.__get_option_output(3)) 
        #print(code_info_list)
        op_dict=dict()
        address = 0
        old_opcode = ""
        cnt = 0
        for opcode in self.get_opcodes().split(" "):
            cnt += 1
            if opcode.startswith("LOG"):
                break
            if opcode.startswith("PUSH"):
                old_opcode = opcode + " "
                cnt+=int(opcode[4:])-1
            else:
                old_opcode+=opcode
                condition = True
                if old_opcode == "INVALID":
                    condition = False
                    op_dict[address]=(old_opcode,(0,0))
                while(condition):
                    node = code_info_list.pop(0)
                    if old_opcode.startswith("PUSH"):
                        if node['name'].startswith("PUSH"):
                            condition = False
                    elif old_opcode == node['name']:
                        condition = False  
                    if not condition:
                        op_dict[address]=(old_opcode,(node['begin'],node['end']))
                    else:
                        pass
                        #print(old_opcode, node['name'],  len(op_dict))
                old_opcode=""
                address += cnt
                cnt = 0
        return op_dict

    
    
    
    
                