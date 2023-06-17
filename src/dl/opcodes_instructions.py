'''
Created on ६ मे, २०१९

@author: JH-ANIC
'''

class EVMOpcodesAndInstructions(object):
    '''
    This class
    '''
    __opcode_details = None
    __file_name = "../../lib/opcodes.txt"
    #__gas_prices = dict()     
    
    
#     @classmethod
#     def get_gas_prices(cls):
#         return cls.__gas_prices
# #     def get_evm_opcodes_and_instructions(self):
# #         if not self.__opcode_details:
# #             self.__load_opcode_information() 
# #         return self.__opcode_details
#     
#     
    @classmethod
    def load_opcode_information(cls):
            """Load information about opcodes"""
            with open(cls.__file_name, 'r') as inputfile:
                cls.__opcode_details = eval(inputfile.read())
                assert(type(cls.__opcode_details)==dict)
            cls.__generate_opcodes_and_instructions()
            #cls.__store_gas_prizes()
            
            
    @classmethod
    def __generate_opcodes_and_instructions(cls):
        #Handle Error..... If opcodes not gets generated
        for opcode_range in ['60-7f-0-5','80-8f-0-3-4-5','90-9f-0-3-4-5']:
            opcode_instruction_details = cls.__opcode_details.get(opcode_range)
            if(opcode_instruction_details == None):
                print("ERROR in file... inputed opcodes file...")
            else:
                opcode_instruction_details = cls.__opcode_details.pop(opcode_range)
                no_of_operations = opcode_range.split('-')
                start = int(no_of_operations.pop(0), 16)
                end = int(no_of_operations.pop(0), 16)
                for i, value in enumerate(range(start, end+1)):
                    temp_information = opcode_instruction_details.copy()
                    for index in no_of_operations:
                        int_index = int(index)
                        temp_information.insert(int_index, temp_information.pop(int_index).replace('*',str(i+1)))
                    cls.__opcode_details[hex(value)[2:]] = temp_information
                    
    
#     @classmethod
#     def __store_gas_prizes(cls):
#         formula = dict()
#         additional = "FORMULA"
#         for opcode in cls.__opcode_details:
#             if opcode == 'Value':
#                 continue
#             opcode_details = cls.__opcode_details.get(opcode)
#             if opcode_details[1] == additional:
#                 formula[opcode_details[0]] = opcode_details[6]
#             else:
#                 cls.__gas_prices[opcode_details[0]] = eval(opcode_details[1])
#         cls.__gas_prices[additional] = formula
#         print(cls.__gas_prices)      
    @classmethod                    
    def get_info(cls, opcode):
        opcode_info = cls.__opcode_details.get(opcode)
        if not opcode_info:
            return None
        __opcode_information =[opcode_info[0], eval(opcode_info[3]), eval(opcode_info[4]), opcode_info[5], opcode_info[8], opcode_info[2], opcode_info[1]]
        #self.find_opcode_type()
        return tuple(__opcode_information)
    
        
#     def find_opcode_type(self):
#         type_info = "O" if self.__opcode_information[1] == 0 else "P"
#         type_info += "O" if self.__opcode_information[2] == 0 else "P"
#         self.__opcode_information.append(type_info)
    