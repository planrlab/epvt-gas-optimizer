'''
Created on on à¥¨à¥­ à¤«à¥‡à¤¬à¥�à¤°à¥�, à¥¨à¥¦à¥§à¥¯
@author: JH-ANIC
'''
import kivy
from kivy.config import Config
Config.set('graphics', 'multisamples', '0')

from _operator import index
kivy.require('1.10.1')
from kivy.animation import Animation
from kivy.properties import ObjectProperty, StringProperty
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.uix.popup import Popup
from kivy.clock import Clock

from src.dl.gas_usage import GasUses
from src.dl.opcodes_instructions import EVMOpcodesAndInstructions


from src.bl.visitor.ast_reader import ASTToCFGObject

from src.bl.optimizer.OPT__Module import OPTModule


from math import ceil, floor, log
from random import choice
import solcx
import threading, time


class SelectDialog(FloatLayout):
    def __init__(self, **kwargs):
        super(SelectDialog, self).__init__(**kwargs)
        self.filechooser.path = "A:\\"
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    
       
class GUI(FloatLayout):
    BYTE_WIDGET_X = 175
    GAS_INFO_WIDGET_Y = 100
    STEP = 0.5
    __index = -1
    __max_length = -1
    file_input = ObjectProperty(None)
    compiled_output = ObjectProperty(None)
    opcode_comment = ObjectProperty(None)
    
    opcodes_list = ObjectProperty(None)
    stack_list = ObjectProperty(None)
    
    memory_list = ObjectProperty(None)
    storage_list = ObjectProperty(None)

    sc_manager = None
    
    instruction_processor = None
    change_from_code = False
    user_input_text = None
    error_message = None
    __stack_memory = None
    __evm_memory = None
    __valid_jump_addresses = []
    __unique_opcodes = set()
    ############
    __STACK_WORD_LIMIT_IN_BYTES = 32
    #################Storage
    contract_information = None
    storage_index_info= None
    sol_source_code = ObjectProperty(None)
    constr_args = StringProperty()
    #fun_list = ListProperty([])
    __toggle = None
    instr_counter = 0

    contract_obj = None
    contracts_list = None
    __source_byte_opcode_map = None
    __constructor_size = None
    __opcode_info = None
    ######
    __is_gui = True
    __ng_opcodes_list = None
    __ng_memory_list = None
    __ng_storage_list = None
    __ng_stack_list = None
    
    ###SM
    __esm = None
    #### Tx
    __transaction = None
    __cfg_builder = None
    __cfg_object = None
    
    def get_cfg_object(self):
        return self.__cfg_object
    
    
    def set_cfg_builder(self, cfg_builder):
        self.__cfg_builder = cfg_builder
        
    
    def get_cfg_builder(self):
        return self.__cfg_builder
    
    
    def read_environment_input(self, call_type):
        #
        callvalue = self.ids.callvalue.text
        self.instruction_processor = InstructionProcessor()
        self.instr_counter = 0
        tx_gas_price = int(self.ids.gas_price.text)
        cnt_address = None
        msg = "Execution in progress"
        if call_type == 'Call':
            selected_function = self.ids.fun_list.text
            print("Selected Function:",selected_function)
            fun_args = self.ids.fun_args.text
            print("Input:",fun_args)
            print("arg_types: ",self.contract_obj.get_ffunctions()[selected_function]['input_types'])
            #self.byte_code = self.sc_manager.helper.get_byte_code()
            self.opcodes_list.adapter.data.extend(self.get_byte_list_code_with_address(0, byte_code = self.contract_obj.get_runtime_bytes()))
            self.__index = -1
            try:
                transaction_data=Encoder(selected_function,(fun_args, self.contract_obj.get_ffunctions()[selected_function]['input_types'])).get_input_string()#fun_sign,args_info
            except Exception as exception:
                self.popup_msg(error=exception)
                return
            else:
                print(transaction_data)
                
            cnt_address = self.ids.cont_acc.text.strip()
            self.__source_byte_opcode_map = self.contract_obj.get_mapping()
            self.__constructor_size = self.contract_obj.get_const_size()

        elif call_type == 'Deploy':
            #self.sc_manager = scm(file_name)
            self.ids.call_btn.disabled = True
            self.ids.fun_list.text = "Select Function"
            self.opcodes_list.adapter.bind(on_selection_change=self.selection_change)
            self.__index = -1
            #self.__instruction = None
            self.__source_byte_opcode_map = self.sc_manager.helper.get_source_mapping()
            #self.selection_counter = 0
            self.sol_source_code.text = self.sc_manager.get_source_code()
            #self.compiled_output.text = self.sc_manager.helper.get_opcodes()
            self.opcodes_list.adapter.data=[]
            self.stack_list.adapter.data.clear()
            self.memory_list.adapter.data.clear()
            self.storage_list.adapter.data=[]
            
            constr_args = self.ids.constr_args.text
            constructor_info = self.sc_manager.get_fconstructor()
            if constructor_info:
                constructor_info=constructor_info['input_types']
            print(constr_args)
            self.__constructor_size = 0
            try:
                transaction_data = Encoder(self.sc_manager.helper.get_byte_code(),(constr_args, constructor_info), method = False).get_input_string()#fun_sign,args_info
            except Exception as exception:
                self.popup_msg(error=exception)
                return 
            self.opcodes_list.adapter.data= self.get_byte_list_code_with_address(start=0,byte_code=transaction_data)
            print("Input data",transaction_data,"Length",len(transaction_data), sep="\n")
            self.temp_contract = self.ids.contract_list.text.strip()
            self.contract_information = dict()
            self.storage_index_info = dict()
            
        self.opcodes_list.scroll_to(0)
        self.opcodes_list._trigger_reset_populate()
        print("\nInput:::", transaction_data)
        self.__max_length = len(self.opcodes_list.adapter.data)-1
        self.stack_list._trigger_reset_populate()
        ###Account Info
        usr_address = self.ids.usr_acc.text
        gaslimit = int(self.ids.gaslimit.text.strip())
               
        #nonce, gas_price, gas_limit, recipient, value, init_data, sender, contract_addr = None
        self.__transaction = Transaction(self.__esm.get_account(usr_address).get_nonce(),# Need to change
                                          tx_gas_price, 
                                          gaslimit,
                                          self.temp_contract,
                                          int(callvalue), #
                                          transaction_data,
                                          usr_address, #sender
                                          usr_address, #origin
                                          cnt_address, # contract address
                                          None)   #signature
        
        self.__esm = self.__transaction.get_esm()
        
        try:
            msg = self.__transaction.start_execution()
            accounts = self.__esm.get_user_accounts()
            accounts.remove(usr_address)
            Transaction.set_miner(choice(accounts))
        except Exception as e:
            self.popup_msg(error = str(e))
            return
        
        self.ids.avl_gas.text = str(self.__transaction.get_remaining_gas())
        
        self.__display_opcode_comments(msg)
        
        self.manage_widget(self.ids.sv_vz, False)
        

    def manage_widget(self, widget_id, vertical = True, special = False):
        length = 0.1
        print(str(widget_id))
        new_size = None
        print("Special", special, vertical)
        
        if special:
            if not self.__toggle:
                self.__toggle = special
            elif self.__toggle != special:
                self.__toggle = special
                return
            
            
            new_size = 900
        if vertical:
            if not new_size:
                new_size = self.GAS_INFO_WIDGET_Y
            Animation(height= new_size if widget_id.height < new_size else length, d=.3, t='out_quart').start(widget_id)
        
        else:
            if not new_size:
                new_size = self.BYTE_WIDGET_X
            print("Ak:: ",widget_id.width, new_size)
            print("Width Check: ", self.ids.sv_vz.width, self.ids.sv_vz.size_hint_x, widget_id.width, self.BYTE_WIDGET_X)
            Animation(width=new_size if widget_id.width < new_size else length, d=.3, t='out_quart').start(widget_id)
           
    
    def on_checkbox_active(self, checkbox, value):
        if value:
            self.ids.cfg_img_widget.source = "../../../lib/img/cfg_src.png"
        else:
            self.ids.cfg_img_widget.source = "../../../lib/img/cfg.png"
        self.ids.cfg_img_widget.reload()   
            
                   
    def selection_change(self, adapter):
        if not self.change_from_code:
            selected = adapter.selection
            if len(selected):
                selected[0].deselect()
            if self.__index>-1: 
                adapter.get_view(self.__index).select()
                self.opcodes_list.scroll_to(self.__index)
        else:
            if self.__index>0:
                adapter.get_view(self.__index-1).deselect()
            if self.__index>-1:
                adapter.get_view(self.__index).select()
            self.opcodes_list.scroll_to(self.__index)
        self.opcodes_list._trigger_reset_populate()
        
            
    def __command_processor(self, msg):
        self.__display_opcode_comments(msg)
        
        
    def __command_executor(self, command):
        pass
    
    
    def __display_opcode_comments(self, text):
            self.opcode_comment.text = text
    
            
    def dismiss_popup(self):
        self._popup.dismiss()
        

    def show_load(self, my_title, my_load):
        content = SelectDialog(load=my_load, cancel=self.dismiss_popup)
        self._popup = Popup(title=my_title, content=content,size_hint=(0.9, 0.9))
        self._popup.open()
        
        
    def __analyze_evm_state(self):
        if not self.__esm:
            EVMOpcodesAndInstructions.load_opcode_information()
            GasUses.load_operation_info()
            EthereumStateMachine.set_ethereum_state(EthereumStateMachine())
        self.__esm = EthereumStateMachine.get_ethereum_state()
        
        
    def select_file(self, path, filename):
        file_name = filename[0]
        self.__analyze_evm_state()
        print("Accounts::",self.__esm.get_accounts())
        print("Hello::",self.__esm.get_accounts())    

        self.file_input.text = file_name    
        self.dismiss_popup()
        
        if filename:
            with open(file_name) as fd:
                source_code = fd.read()
            self.sol_source_code.text = source_code  
            #self.compile_solidity_source_code(source_code, file_name[file_name.rindex('\\')+1:])
            self.popup_msg("File Loaded Successfully")
    
    
    def compile_solidity_source_code(self, source_code):
        if not self.sc_manager:
            self.sc_manager = scm(source_code)
        else:
            self.sc_manager.set_source_code(source_code)
        
        self.sol_source_code.text = self.sc_manager.get_source_code()
        self.ids.contract_list.text = self.sc_manager.helper.get_contracts_list()[0]
        
        self.ids.constr_args.readonly = False
        constructor = self.sc_manager.get_fconstructor()
        
        if constructor:
            self.ids.constr_args.text = ','.join(constructor['input_types'])
        else:
            self.ids.constr_args.text = ""
            self.ids.constr_args.readonly = True
            
        self.ids.contract_list.values = self.sc_manager.helper.get_contracts_list()
        self.opcodes_list.adapter.data.clear()
        self.stack_list.adapter.data.clear()
        self.memory_list.adapter.data.clear()
        self.opcodes_list.adapter.bind(on_selection_change=self.selection_change)
        
        self.ids.call_btn.disabled = True
        self.reload_accounts()
    
            
    def select_next(self, time = None):
        arguments = self.instruction_processor.process_instruction()
        print("Check",arguments, " => Arguments")
        return self.perform_task(arguments)
    
          
    def perform_task(self, arguments):
        msg = "Done"
        code = arguments[0]
        
        if code >= 0:
            if code == 0:
                msg = self.__next_opcode(1) 
                self.instr_counter += 1
                 
                       
            elif code == 2:
                opcodes = "Error on stack"
                if arguments[1] == 0: # from fetch from OPL
                    opcodes = ""
                    for _ in range(arguments[2]):
                        opcodes += self.__next_opcode()
                    msg = self.instruction_processor.get_message(2, opcodes)
                    
                elif arguments[1] == 1: # from input environment
                    operation_code = arguments[2]
                    
                    if operation_code == 0: #CALLVALUE
                        opcodes = hex(self.__transaction.get_call_value())[2:].zfill(64)
                    
                    elif operation_code == 1: #CALLDATASIZE
                        opcodes = hex(len(self.__transaction.get_transaction_data())//2)[2:].zfill(64)
                    
                    elif operation_code == 2: #CALLDATALOAD
                        x = arguments[3]
                        opcodes = self.__transaction.get_transaction_data()[2*x:2*(32+x)].ljust(64,'0')
                    
                    elif operation_code == 3: #CODESIZE
                        opcodes = hex(len(self.__transaction.get_transaction_data())//2)[2:].zfill(64)
                        
                    elif operation_code == 4: #Address
                        opcodes = self.__transaction.get_contract_addr()[2:].zfill(64)
                        
                    elif operation_code == 5: #Balance
                        opcodes = hex(self.__esm.get_account(arguments[3]).get_balance())[2:]
                    
                    elif operation_code == 6: #ORIGIN
                        opcodes = self.__transaction.get_sender()[2:].zfill(64)#address
                        
                    elif operation_code == 7: #CALLER
                        opcodes = self.__transaction.get_sender()[2:].zfill(64)
                        
                    elif operation_code == 8: #EXTCODESIZE
                        opcodes = hex(self.__esm.get_account("0x"+arguments[3][-40:]).get_code_size())[2:]
#                         input("verify Extcodesize::"+opcodes)
                    
                    elif operation_code == 9: #GASPRICE
                        opcodes = hex(self.__transaction.get_gas_price())[2:]
                        
                    elif operation_code == 10: #GAS
                        opcodes = hex(self.__transaction.get_remaining_gas())[2:]
                        
                    elif operation_code == 11: #RETURNDATASIZE
                        opcodes = hex(len(self.__transaction.get_output_data())//2)[2:]
                        
                    
                    msg = self.instruction_processor.get_message(2, opcodes)

                elif arguments[1] == 2: # from runtime calculation like comp_bit_logic
                    opcodes = arguments[2]
                    msg = self.instruction_processor.get_message(3)
                
                else:
                    print("Need to Implement")
                
                if type(opcodes)== str:
                    self.__perform_stack_push(opcodes, 0)
                else:
                    for item in opcodes:
                        self.__perform_stack_push(item, 0)
                        
            elif code == 1:
                opcode = self.__perform_stack_pop()#.lstrip('0')
                msg = self.instruction_processor.get_message(1, opcode)
            
            elif code == 3:#Other Operations(EVM)......
                if len(arguments)>1:
                    result = self.__perform_evm_memory_operations(arguments[1])
                    if result:
                        self.__perform_stack_push(result)
                msg = self.instruction_processor.get_message(3)
            
            elif code == 4:#SPECIAL INSTRUCTIONS
                code = arguments[1]
                
                if code == -2: #NO_OPERATION 
                    print("ERROR IN YOUR CODE.... STOP EXECUTION")
                    self.pause_execution()
                    self.popup_msg(error="INVALID OPCODE\nError occurred during execution...")
                    self.reset_current()
                    self.reload_accounts()
                    self.manage_widget(self.ids.sv_vz, False)
                    self.__esm = EthereumStateMachine.get_ethereum_state() # What about used gas till INVALID instruction?
                
                elif code == -1: #NO_OPERATION 
                    '''NOT ON GUI'''
                    print("Valid destination for jumps:", arguments[2])
                    self.__valid_jump_addresses.append(arguments[1])
                    msg = self.instruction_processor.get_message(code)
                
                elif code == 0: # MODIFY PC
                    print("OLD: ", self.__index, ",", arguments[2])
                    self.__index += arguments[2]
                    msg = self.instruction_processor.get_message(3)
                
                elif code == 1: #SHA operation
                    from sha3 import keccak_256
                    print("Performing Crypto CAT operations")
                    start,end = arguments[2]
                    ext_info = ""
                    memory_list = self.memory_list.adapter.data if self.__is_gui else self.__ng_memory_list
                    for member in memory_list[start//16:(end//16)+1]:
                        ext_info+=member.split(":")[1]
                    hex_info = ext_info[(start%16)*2:((start%16)+(end-start+1))*2] 
                    self.__perform_stack_push(keccak_256(bytes.fromhex(hex_info)).hexdigest())
                    #hex_info="b10e2d527612073b26eecdfd717e6a320cf44b4afac2b0732d9fcbe2b7fa0cf6"
                    
            elif code == 5:#SYS INSTRUCTIONS
                code = arguments[1]
                if code == 0:
                    if self.__is_gui:
                        self.__index = -1
                        self.opcode_comment.text = "Displays Comments"
                        pmsg ="Message call executed successfully...\nInstructions Executed:: "+str(self.instr_counter) +"\nGas Used:: "+str(self.__transaction.get_total_gas_used())
                        self.popup_msg(pmsg)
                        self.pause_execution()
                        print("No of instructions executed", self.instr_counter)
                        self.reset_current()
                        self.manage_widget(self.ids.sv_vz, False)
                        
                        self.opcodes_list.adapter.data=[]
                        self.stack_list.adapter.data=[]
                        self.memory_list.adapter.data=[]
                        self.stack_list._trigger_reset_populate()
                        self.memory_list._trigger_reset_populate()
                        #self.pause_execution()
                        self.__transaction.finalize_state()
                        self.reload_accounts()
                    else:
                        return "1"
                    
                elif code == 1: #RETURN
                    msg = self.instruction_processor.get_message(3)
                    #print(arguments[2],arguments[3],list(self.memory_list.adapter.data))
                    #input("Waiting")
                    memory_list = self.memory_list.adapter.data if self.__is_gui else self.__ng_memory_list
                    
                    return_code = self.get_code_from_list(memory_list[floor(arguments[2]/16):ceil((arguments[2]+arguments[3])/16)], arguments[2]%16, arguments[3])
                    pmsg = None
                    if not self.__transaction.get_contract_addr():
                        print("Dcheck:",self.storage_index_info,"\n",self.contract_information)
                        """self.__transaction.is_sufficient_gas(mnemonic, args)len(runtime_bytes) * GasUses.get_price("Gcodedeposit")  
                        """
                        ###
                        cost = GasUses.get_price("Gcodedeposit") * len(return_code)//2
                        F = (self.__esm == None and return_code == "") or self.__transaction.get_remaining_gas() < cost or (len(return_code)//2) > 24576
                        
                        self.__transaction.set_remaining_gas(0 if F else self.__transaction.get_remaining_gas() - cost)
                        
                        account = self.sc_manager.deploy_contract(self.__transaction.generate_new_address(), return_code, (self.storage_index_info, self.contract_information), self.__index+2, self.temp_contract, balance=0)    
                        print("Constructor Code size::",self.__index, hex(self.__index))
                        print("asdw", return_code, account,sep="\n")
                        #input("Cheas")
                        self.__esm.add_account(account.get_address(), account)
                        ##Reset Constructor Deploy
                        #input("Check1:")
                        if self.__is_gui:
                            constructor_obj = self.sc_manager.get_fconstructor()
                            self.ids.constr_args.text = ','.join(constructor_obj['input_types']) if constructor_obj else ""
                            pmsg = "Contract Deployed Successfully and \nAvailable under Contract addresses list\n No of instructions executed:: "
                        else:
                            print("IN ELSE", account, type(account))
                            #self.__transaction.set_output_data(return_code)
                            #input("Check2:")
                            return account
                    
                    
                    if self.__is_gui:
                        if not pmsg:
                            pmsg = "Work on Decoder is under progress\n"
                        pmsg += "Instructions Executed:: "+str(self.instr_counter) +"\nGas Used:: "+str(self.__transaction.get_total_gas_used())
                        self.popup_msg(pmsg)
                        self.pause_execution()
                        print("No of instructions executed", self.instr_counter)
                        print("Executed Opcodes::", self.instruction_processor.get_executed_opcodes())
                        print("Gas Used::", self.__transaction.get_total_gas_used())
                        self.reset_current()
                        self.manage_widget(self.ids.sv_vz, False)
                        
                    else:
                        print("It is not user message_call", return_code)
                        
                        return return_code    
                        
                    self.__transaction.finalize_state()
                        
                    self.reload_accounts()
                    msg = "Work in progress on this functionality..."
                    
                    
                elif code == 2: #CREATE
                    ERROR_CODE = "0"
                    MAX_DEPTH_LIMIT = 1024
                    operands = arguments[2]
                    
                    ### whose balance?    transaction_callers_available or origin_available
                    curr_bal =  self.__transaction.get_sender_account().get_balance()  #Contract or User acc
                    req_bal = int(operands[0],16)
                    
                    #SCM should handle this...
                    curr_depth= 1 # Need to provide functionality to get current depth limit
                    
                    error_condition = curr_bal<req_bal or curr_depth == MAX_DEPTH_LIMIT #or Exceptional_Halt_Condition
                    print(error_condition, operands, sep="\n")
                    
                    #input("Need to check...")
                    if error_condition:
                        self.__perform_stack_push(ERROR_CODE)
                    else:
                        """CREATE NEW ACCOUNT"""
                        start = int(operands[1],16)
                        end  = int(operands[2],16)
                        self.pause_execution()
                        f_start =  start//16
                        f_end = ceil((start+end)/16)
                        start %= 16
                        end += start
                        memory_list = self.memory_list.adapter.data if self.__is_gui else self.__ng_memory_list
                        
                        associated_code = ''.join([memory_list[mem_pos].split(":")[1].strip() for mem_pos in range(f_start, f_end)])[2*start: 2*(start + end)]
                        
                        #print(associated_code,"\n actual Byte code size..", hex(len(associated_code)))
                        #input("Wait recheck")
                        
                        print(self.limit, self.sol_source_code.text, sep = "\n=====\n")
#                         input("Checking...." + self.sol_source_code.selection_text)
                        
                        #adjust = self.sol_source_code.text[:self.limit[0]].count('\n')
                        #self.limit = list(map(lambda x: x-adjust, self.limit))
                        temp_contract = self.sol_source_code.text[self.limit[0]:self.limit[1]].split("new ")[1]
                        temp_contract = temp_contract[:temp_contract.index("(")]
                        
                        #print("Selected Contract: ", type(self.sol_source_code.selection_text), sep="\n")
                        print("IS IT", temp_contract, associated_code, len(associated_code), sep="\n")
                        
                        new_account = self.create_contract(req_bal, associated_code, temp_contract)
#  UPDATED IN TX                      curr_addr = self.cnt_address
#  UPDATED IN TX                       caller = self.__esm.get_account("0x"+curr_addr)
                        """New Account should be created based on the current nonce value and callers address
                           Need to modify following called functions definition based on the actual logic of creating new account address
                        """
                        """Nonce needs to be increment based on XX"""
                        #Change name of function Nonce value increment #Even on function call required this
                        self.__perform_stack_push(new_account)

                    msg = self.instruction_processor.get_message(3)
                
                elif code == 3:
                    #Clock.unschedule(self.opcode_processor)
                    self.__perform_stack_push(self.__perform_call_operation(arguments[2]))
                    msg = self.instruction_processor.get_message(3)
                    
                
            elif code == 6:#Storage Memory
                msg = self.__perform_storage_operations(arguments)
            self.__display_opcode_comments(msg)
                
        else:
            input("Invalid Code Received from Instruction Processor.........") 
    
    
    def load_contract(self, address):
        contract_account = self.__esm.get_account(address)
        self.contract_obj = contract_account
        constructor_obj = contract_account.get_fconstructor()
        self.ids.constr_args.text = ','.join(constructor_obj['input_types']) if constructor_obj else ""
        
        self.ids.fun_list.text = 'Select Function'
        self.ids.fun_list.values = list(contract_account.get_ffunctions().keys())
        
        self.sol_source_code.text = contract_account.get_source_code()
        #self.compiled_output.text = contract_account.get_opcodes()
        #self.opcodes_list.adapter.data.extend(contract_account.get_runtime_bytes())
        self.__max_length = len(self.opcodes_list.adapter.data)-1
        self.opcodes_list.scroll_to(0)
        
        ###Load Memory contents#######
        self.storage_list.adapter.data = []
        
        self.storage_index_info = contract_account.get_storage_info().get_sm_index_info()
        self.contract_information = contract_account.get_storage_info().get_s_memory()
        
        self.storage_list.adapter.data = [""]*len(self.storage_index_info)
        ### Dont use append since index is fixed with respect to its object in GUI view
        
        self.ids.call_btn.disabled = True
        
        for key in self.contract_information:
            self.storage_list.adapter.data[self.storage_index_info[key]]=(key+":"+self.contract_information[key])
        
        
        #print(contract_obj.get_ffunctions())
        #print("Verify Details",self.sc_manager.get_ffunctions(), sep="\n")
        
    def reset_view(self,cls,pos=0): 
        cls.operand_list.adapter.get_view(pos).select()
        cls.operand_list._trigger_reset_populate()
        
    def popup_msg(self, msg="", error = None, reset = 1):
        if not error:
            if reset:
                my_title = ">>>>>> SUCCESS <<<<<<"
            else:
                my_title = ">>>>>> WARNING <<<<<<"
            #txt_color = (0,1,0,1)
            bg_color = (0, 0, 0, 1)
        else:
            error = str(error).replace("name", "value")
            if reset:
                self.reset_current()
            msg = error.replace("defined", "valid")
            my_title = ">>>>>> ERROR <<<<<<" 
            #txt_color = (0,1,0,1)
            bg_color = (1, 1, 1, 1)
            print(msg, type(msg),"\n")
            
        txt_color = (0,1,0,1)
        layout = BoxLayout(orientation='vertical')
        l = Label()
        l.text=msg
        l.color=txt_color
        l.background_color= bg_color
        l.font_size='20sp'
        l.text_size= self.width, None
        l.size_hint=(1, None)
        l.bind(width=lambda *x: l.setter('text_size')(l, (l.width, None)))        
        layout.add_widget(l)
        close_button = Button(text = "OK", size_hint=(.3,.2), pos_hint={'center_x': .5, 'center_y': 0})
        layout.add_widget(close_button)
        self._popup = Popup(title=my_title, title_size= (30), 
                  title_align = 'center', content = layout,
                  size_hint=(None, None), size=(500, 400),
                  auto_dismiss = False)
        close_button.bind(on_press=self._popup.dismiss)
        self._popup.open()
        mythread = threading.Thread(target=self.poptest)
        
        
    def poptest(self):
        time.sleep(3)
        self._popup.dismiss()
        
            
    def load_user_input(self, input_label):
        content = BoxLayout(orientation="horizontal")
        label = Label(text=input_label)
        self.user_input_text = TextInput(hint_text='Enter Input here',font_size=12,focus=True)
        button = Button(text = "Save")
        self.error_message = Label(text ="", color = [0.964, 0.054, 0.054, 1])
        self.error_message.disabled = True
        content.add_widget(label)
        content.add_widget(self.user_input_text)
        content.add_widget(button)
        content.add_widget(self.error_message)
        self._popup = Popup(title=input_label, content=content, size_hint=(0.9, 0.2))
        self._popup.open()
        button.bind(on_press=self.save_input)
    
    
    def save_input(self, *args):
        print(args)
        if self.user_input_text:
            input_text = self.user_input_text.text.strip()
            print("User Input Text: ", input_text)
            try:        
                self.user_input_text = int(input_text, 10)
            except:
                self.error_message.text = "Not a valid Input"
                self.error_message.disabled = False


    def __perform_storage_operations(self, arguments):
        code = arguments[1]
        
        if code == 1:#STORE
            s_index, data = arguments[2]
            """Contract Info"""
            self.contract_information[hex(s_index)] = data
            pos = self.storage_index_info.get(hex(s_index))
            storage = self.storage_list.adapter.data if self.__is_gui else self.__ng_storage_list
            
            if pos is None:
                pos = len(storage)
                self.storage_index_info[hex(s_index)] = pos
                storage.append(hex(s_index)+":"+data)
            else:
                storage[pos] = hex(s_index)+":"+data
            
            if self.__is_gui:
                self.storage_list.adapter.get_view(pos).select()
                self.storage_list._trigger_reset_populate()
            
            ########    GAS    COMP    ###
            #self.__transaction.update_gas(operation = self.instruction_processor.get_mnemonic(), args = (length, arguments[2]))
            
            return "Stored "+hex(int(data,16))+" in Storage"
        
        elif code == 2: #LOAD """"STORAGE INFO NOT HANDLED HERE...........
            s_index = arguments[2]
            data = self.contract_information.get(hex(s_index))
            if data and self.__is_gui:
                self.storage_list.adapter.get_view(self.storage_index_info.get(hex(s_index))).select()
            elif not data:
                data = '0' * 64
            self.__perform_stack_push(data)        
            return "Loaded "+hex(int(data,16))+" from Storage"
    
    
    def __perform_evm_memory_operations(self, instruction):
        print("Instruction::", instruction)
        operation, location, data = instruction
        
        memory_list = self.memory_list.adapter.data if self.__is_gui else self.__ng_memory_list
        length = len(memory_list)
        
        def code_copy(code=None):
            #Clock.unschedule(self.opcode_processor)
            nonlocal length, memory_list, data, location
            if length <= location:
                memory_list.extend(self.update_evm_memory_view(location+1, length))
            offset = int(data[0],16)
            total_bytes = int(data[1],16)
            
            if not code:
                code = self.__transaction.get_transaction_data()
                
            code = code[offset*2:(offset+total_bytes)*2]
            
            nibbles_to_append = len(code)%64
            if nibbles_to_append:
                code = code.ljust(len(code)+64-nibbles_to_append,"0")
                
            opcodes = self.get_byte_list_code_with_address(0, evm = 1, loc = location, byte_code=code)
            print("Check:",opcodes,sep="\n")
            length = len(memory_list)
            for pos, val in enumerate(opcodes):
                if length>location+pos:
                    memory_list[location+pos] = val
                else:
                    memory_list.insert(location+pos, val)

        
        def store_data_to_memory_updated(end=None, mem_data=None):
            nonlocal length, memory_list, data, location
#             print("Len:", length)
#             input("Checking...")
            start = int(data[0],16)
            
            if data[1]:
                end = int(data[1],16)+start

            if not mem_data:
                mem_data = self.__transaction.get_transaction_data()
            
            if length <= location:
                memory_list.extend(self.update_evm_memory_view(location+1, length))
            new_length = len(memory_list)
#             print(length, memory_list, data, location, new_length, end, mem_data, sep="\n===\n")
            
            opcodes = self.get_byte_list_code_with_address(start, end, evm = 1, loc = location, byte_code=mem_data)
            
            print(opcodes)
#             input("Verify Opcodes")
            for pos, val in enumerate(opcodes):
                if new_length > location+pos:
                    _,new_data = val.split(":")
                    new_data = new_data.strip()
                    if len(new_data)<32:
                        contents = memory_list[location+pos]
                        address, data = contents.split(":")
                        val = address + " : " + new_data + data.strip()[len(new_data):]
                        memory_list[location+pos] = val
                    else:
                        memory_list[location+pos] = val
                else:
                    memory_list.insert(location+pos, val)

            print(memory_list)
            
        if operation == 0:
            location_offset = location%16
            location = location//16
            
            if length >= location:
                data = memory_list[location].split(":")[1].strip()[location_offset*2:].strip()
                print(memory_list[location].split(":")[1],data,sep="\n")
                data += memory_list[location+1].split(":")[1].strip()
                if location_offset:
                    data+=memory_list[location+2].split(":")[1].strip()[:location_offset*2]
                    print("Verify::",data)
                self.__perform_stack_push(data)
            else:
                input("Error... do verify")    
        
        
        elif operation == 1:
            """
            Logic changed.... Need to remove extra variable (location_index)
            """
            location_offset = location%16
            location = location//16
            length = len(memory_list)
            
            condition = location+ (3 if location_offset else 1)
            print(location, condition, length, "Check")
            if length <= condition:
                memory_list.extend(self.update_evm_memory_view(condition, length))
            
            if location_offset:
                l,v = memory_list[location].split(":")
                memory_list[location]=l+": "+v.strip()[:location_offset*2]+data[:32-(location_offset*2)]
                
                memory_list[location+1]=memory_list[location+1].split(":")[0].strip()+": "+data[32-(location_offset*2):64-(location_offset*2)]
                
                l,v = memory_list[location+2].split(":")
                memory_list[location+2]=l+": "+data[64-(location_offset*2):]+v.strip()[(location_offset*2)-32:]
                
            else:
                memory_list[location]=memory_list[location].split(":")[0].strip()+": "+data[:32]
                memory_list[location+1]=memory_list[location+1].split(":")[0].strip()+": "+data[32:]
            
            print("ML_::", memory_list)
#             expanded_memory = ceil((len(memory_list)-length)/2)
#             if expanded_memory:
#                 self.__transaction.update_gas(operation = 'Gmemory', units = expanded_memory)
                  
        elif operation == 2:
            """Update Section"""
            bytes_to_copy = None
            if self.__transaction.get_contract_addr():
                bytes_to_copy = self.contract_obj.get_runtime_bytes()
                print(bytes_to_copy)
            code_copy(bytes_to_copy)
                                
        elif operation == 3:
            store_data_to_memory_updated()         

        elif operation == 4:#EXTCODECOPY
            print(location)
            account = data.pop(0)
            print("Account?:",account)
            print(data)
            account_code = self.__esm.get_account("0x"+account[-40:]).get_runtime_bytes()
            print("Account code::", account_code)
#             input("TBA... IN SCVM")
            store_data_to_memory_updated(mem_data = account_code)
        
        elif operation == 5:#RETURNDATACOPY
            print("Data to store in memory:: ", self.__transaction.get_output_data())
            store_data_to_memory_updated(mem_data = self.__transaction.get_output_data())
            
            
        if self.__is_gui:
            self.memory_list._trigger_reset_populate()
            self.memory_list.adapter.get_view(location).select()
            self.memory_list.adapter.get_view(location+1).select()
            if location-5 > -1:
                location = location - 5
            else:
                location = 0
            self.memory_list.scroll_to(location)

    #MSG_CALL
    def __perform_call_operation(self, parameters):
        
        memory_backup = None if self.__is_gui else \
            (self.__ng_opcodes_list, self.__ng_stack_list, self.__ng_memory_list)
        
        print("Backing UP")
        print((self.temp_contract, self.__constructor_size, self.__transaction.get_transaction_data()),(self.__index, self.__max_length, self.instruction_processor), memory_backup, (self.storage_index_info, self.contract_information))
        print("DOne BUP")
        
        self.sc_manager.push_execution_environment(((self.temp_contract, self.__constructor_size, self.__transaction),(self.__index, self.__max_length, self.instruction_processor), memory_backup, (self.storage_index_info, self.contract_information)))
        
        
        """
        code 0: CALL
        code 1: CALLCODE
        code 2: DELEGATECALL
        code 3: STATICCALL
        """
        code, parameters = parameters
        
        if code == 0:
            pass
        
        elif code == 1:
            pass
        
        elif code == 2:
            pass
        
        elif code == 3:
            parameters.insert(2, "0")
            
        else:
            raise Exception("Invalid code value "+str(code))
        
        
        memory_list = self.memory_list.adapter.data if self.__is_gui else self.__ng_memory_list
                    
        """
        ###Input Data,
        """
        gas_available = int(parameters[0], 16)
        to = "0x"+parameters[1][-40:]
        value = int(parameters[2], 16) 
        in_offset = int(parameters[3], 16)
        in_size = int(parameters[4], 16)
        out_offset = int(parameters[5], 16) 
        out_size = int(parameters[6], 16)
        
        input_data = self.get_code_from_list(memory_list[floor(in_offset/16):ceil((in_offset + in_size)/16)], in_offset%16, in_size)
        
        self.__transaction = Transaction( None, #self.__transaction.get_nonce(),#user_account
                                          self.__transaction.get_gas_price(), 
                                          gas_available, #self.__transaction.get_gas_limit(),
                                          to,#
                                          value, #value
                                          input_data,#data
                                          self.__transaction.get_contract_addr(), #sender
                                          self.__transaction.get_sender(), #origin
                                          self.__transaction.get_contract_addr(), # contract_addr
                                          None) # signature
        
       
        #self.__transaction.get_sender_account().incr_nonce()
        print(self.__esm.get_accounts(), to, sep="\n")
        recipient  = self.__esm.get_account(to) 
        self.temp_contract = to
        contract_byte_code = recipient.get_runtime_bytes()
        print("Runtime bytes.....", contract_byte_code)
        #self.transaction_data = contract_byte_code
        print("input data:: ", input_data)
        contract_byte_code += input_data
        self.__index = -1
        self.instruction_processor = InstructionProcessor()
        self.__is_gui = False
        self.__constructor_size = recipient.get_const_size()
        self.__ng_stack_list = []
        self.__ng_memory_list = []
        #self.__ng_storage_list = 
        
        self.__ng_opcodes_list= self.get_byte_list_code_with_address(start=0,byte_code=contract_byte_code)
        self.__max_length = len(self.__ng_opcodes_list) - 1#with address
        
        self.storage_index_info = recipient.get_storage_info().get_sm_index_info()
        self.contract_information = recipient.get_storage_info().get_s_memory()
                 
        self.__source_byte_opcode_map = recipient.get_mapping()
        print(self.__source_byte_opcode_map, len(self.__source_byte_opcode_map), sep="\n")
#         input("Recheck Mapping.....")
        return_data = None
        
        
        Clock.unschedule(self.opcode_processor)
        try:
            while self.__index < self.__max_length-1:
                return_data = self.select_next()           
                if return_data:
                    break
                
        except Exception as e:
            self.popup_msg(error=e, reset = 0) #Execution must continue
            return_data = "0"   
        
        Clock.unschedule(self.opcode_processor)
        
        print(self.__esm.get_contract_accounts())
        print("Return Data::::", return_data)
        #print("EVm_Memory:::", self.__ng_memory_list)
        
        ((self.temp_contract, self.__constructor_size, self.__transaction),(self.__index, self.__max_length, self.instruction_processor), memory_backup, (self.storage_index_info, self.contract_information)) = self.sc_manager.pop_execution_environment()
        
        self.__transaction.set_output_data(return_data) 
        n = min((len(return_data), out_size))
        
        if memory_backup:
            (self.__ng_opcodes_list, self.__ng_stack_list, self.__ng_memory_list) = memory_backup
            self.__ng_storage_list = []
            self.__is_gui = False
            #self.__ng_memory_list.
        else:
            #Store something at location offset
            self.__is_gui = True
        
            
        self.__perform_evm_memory_operations((5, out_offset//16, ("0", hex(n)[2:])))
            
        self.__source_byte_opcode_map = self.__transaction.get_contract_account().get_mapping()
        

        return return_data if return_data == "0" else "1"
    
    
    
    def create_contract(self, req_bal, contract_byte_code, contract_name):
        memory_backup = None
        
        if self.__is_gui:
            memory_backup = None
            
        else:
            memory_backup = (self.__ng_opcodes_list, self.__ng_stack_list, self.__ng_memory_list)
        
        print((self.temp_contract, self.__constructor_size, self.__transaction.get_transaction_data()),(self.__index, self.__max_length, self.instruction_processor), memory_backup, (self.storage_index_info, self.contract_information))
    
        self.sc_manager.push_execution_environment(((self.temp_contract, self.__constructor_size, self.__transaction),(self.__index, self.__max_length, self.instruction_processor), memory_backup, (self.storage_index_info, self.contract_information)))
        
        self.__transaction = Transaction(self.__transaction.get_contract_account().get_nonce(),
                                          self.__transaction.get_gas_price(), 
                                          self.__transaction.get_gas_limit(),
                                          contract_name,#
                                          req_bal, #value
                                          contract_byte_code,#data
                                          self.__transaction.get_contract_addr(), #sender
                                          self.__transaction.get_sender(), #origin
                                          None, # contract_addr
                                          None) # signature
        
        ##INC NONCE
        self.__transaction.get_sender_account().incr_nonce()
        
        self.temp_contract = contract_name
        #self.transaction_data = contract_byte_code
        self.__index = -1
        self.instruction_processor = InstructionProcessor()
        self.__is_gui = False
        self.__constructor_size = 0
        #self.call_type = "Deploy"
        self.__ng_stack_list = []
        self.__ng_memory_list = []
        self.__ng_storage_list = []
        
        self.__ng_opcodes_list= self.get_byte_list_code_with_address(start=0,byte_code=contract_byte_code)
        self.__max_length = len(self.__ng_opcodes_list) - 1#with address
        
        self.storage_index_info = dict()
        self.contract_information = dict()
        
        self.sc_manager.helper.set_contract(contract_name)
        self.__source_byte_opcode_map = self.sc_manager.helper.get_source_mapping()
        
        account = None
        
        try:
            while self.__index < self.__max_length-1:
                account = self.select_next()           
                if account:
                    break
        except Exception as e:
            self.popup_msg(error = e, reset = 0) #Execution must continue
            account = "0"
            print("Error Occurred ...", e)
            
        print(account, type(account))
                
        print("Account address::::", account.get_address())
        contract_address = account.get_address()[2:] if account!="0" else "0"*40
        print(self.__esm.get_contract_accounts())
        
        ((self.temp_contract, self.__constructor_size, self.__transaction),(self.__index, self.__max_length, self.instruction_processor), memory_backup, (self.storage_index_info, self.contract_information)) = self.sc_manager.pop_execution_environment()
        
        if memory_backup:
            (self.__ng_opcodes_list, self.__ng_stack_list, self.__ng_memory_list) = memory_backup
            self.__ng_storage_list = []
            self.__is_gui = False
        else:
            self.__is_gui = True
        self.sc_manager.helper.set_contract(self.temp_contract)    
        self.__source_byte_opcode_map = self.sc_manager.helper.get_source_mapping()
        return contract_address
        
        
    def change_address(self, new_address):
        self.ids.deploy_btn.disabled = False 
        self.ids.gaslimit.text = str(self.__esm.get_account(new_address).get_balance())
        self.ids.avl_gas.text = self.ids.gaslimit.text
        self.enable_trans_call()
        
    def change_contract(self, contract_name):
        self.sc_manager.reload_methods(contract_name.strip())
        constructor_obj = self.sc_manager.get_fconstructor()
        self.ids.constr_args.text = ','.join(constructor_obj['input_types']) if constructor_obj else ""
        self.ids.fun_list.text = "Select Function"
        #self.ids.fun_list.values = list(self.sc_manager.get_ffunctions().keys())
        self.enable_trans_call()
    
    def __perform_stack_push(self, data, pos=0):
        if self.__is_gui:
            self.stack_list.adapter.data.insert(pos,data.zfill(2*self.__STACK_WORD_LIMIT_IN_BYTES))
            self.stack_list.adapter.get_view(pos).select()
            self.stack_list._trigger_reset_populate()
        else:
            self.__ng_stack_list.insert(pos,data.zfill(2*self.__STACK_WORD_LIMIT_IN_BYTES))
               
    
    def __perform_stack_pop(self):
        #self.stack_list.adapter._trigger_layout()
        data = self.stack_list.adapter.data if self.__is_gui else self.__ng_stack_list
        popped_data = None
        if len(data)>0:
            popped_data = data.pop(0)           
        else:
            input("Handle Empty Stack Error....")
        
        if self.__is_gui:
            if len(data)>0:
                self.stack_list.adapter.get_view(0).select()
            self.stack_list._trigger_reset_populate()
        return popped_data
    
    
    def __next_opcode(self, is_instruction = None):
        self.change_from_code = True
        self.__index+=1
        ## Selection equivalent assembly code 
        if self.__is_gui:
            self.opcodes_list.adapter.get_view(self.__index).trigger_action(duration=0)
            self.opcodes_list.scroll_to(self.__index)
               
        if is_instruction:
            self.ids.avl_gas.text =  str(self.__transaction.get_remaining_gas())
            
            opcode = self.opcodes_list.adapter.get_view(self.__index).text.lstrip("0x").split(':') if self.__is_gui else self.__ng_opcodes_list[self.__index].lstrip("0x").split(':')
            print("OPCODES:::", opcode)
            self.instruction_processor.set_instruction(opcode)
            
            required_gas = self.get_req_gas()
            print("Required GAS::", required_gas, "Opcode", opcode)
            total_required_gas = sum(required_gas)
            
            self.ids.mn_g.text = str(required_gas[0])
            self.ids.me_g.text = str(required_gas[1])
            self.ids.req_gas.text = str(total_required_gas)

            print("Available:: "+str(self.__transaction.get_remaining_gas()),"\nmnemonic::", self.instruction_processor.get_mnemonic())            
            self.__transaction.is_sufficient_gas(total_required_gas)
            msg = self.instruction_processor.get_message(0)
            self.__unique_opcodes.add(opcode[1].strip())
            self.limit = list(self.__source_byte_opcode_map[self.__index + self.__constructor_size][1])  #returns (text, limit)
#             PROPER MESSAGING LOGIC....    
#             text, operand = text.split(" ") if " " in text else (text, None)
#             self.__opcode_info = (operand+" :: "+msg) if operand else (" :: "+msg)
            print(self.instruction_processor.get_mnemonic())
            print(self.limit[0], self.limit[1], self.sol_source_code.text[self.limit[0]:self.limit[1]], sep = "$$$")            
            """
            No need to call ADJUST
            self.adjust()
            """
            self.compiled_output.text = self.instruction_processor.get_mnemonic()#text[:text.index(" ") if " " in text else None] #Modified to only opcode
            #print("ch:", text)
            self.sol_source_code.focus = True
            self.sol_source_code.select_text(self.limit[0], self.limit[1]+1)            
            #self.sol_source_code.use_handles = True
            #self.sol_source_code.cursor = (self.sol_source_code.get_cursor_from_index(limit[1]))
            return msg        
        else:
#             PROPER MESSAGING LOGIC....
#             if self.__opcode_info:
#                 self.compiled_output.text +=" "+self.__opcode_info
#                 self.__opcode_info = None
            self.sol_source_code.select_text(self.limit[0], self.limit[1]+1)
            return self.opcodes_list.adapter.get_view(self.__index).text.lstrip("0x").split(':')[1].strip() if self.__is_gui else self.__ng_opcodes_list[self.__index].lstrip("0x").split(':')[1].strip()
            #return self.opcodes_list.adapter.get_view(self.__index).text.lstrip("0x").split(':')[1].strip()
    
    
    def adjust(self):
        if self.limit[0]:
            adj = self.sol_source_code.text[:self.limit[0]].count("\n")
            self.limit[0] -= adj
            self.limit[1] -= adj
            print("mod* ", self.limit)
            text = self.sol_source_code.text[self.limit[0]:self.limit[1]+1]
            adj = len(text) - len(text.lstrip()) 
            self.limit[0] += adj
            self.limit[1] += adj
            adj = self.sol_source_code.text[self.limit[0]:self.limit[1]+1].count("\n")
            self.limit[1] -= adj
            
            
    def opcode_processor(self, t):
        if self.__index > self.__max_length-1:
            Clock.unschedule(self.opcode_processor)
        else:
            print(self.__index , self.__max_length)
            self.select_next()
    
    
    def enable_trans_call(self):
        if self.ids.usr_acc.text.startswith("0x"):
            self.ids.deploy_btn.disabled = False
            if self.ids.cont_acc.text.startswith("0x") and " " not in self.ids.fun_list.text:
                self.ids.call_btn.disabled = False 
        else:
            self.ids.deploy_btn.disabled = True
            self.ids.call_btn.disabled = True
    
    
    def execute_all(self):
        Clock.schedule_interval(self.opcode_processor, self.ids.pb.value)
    
    
    def pause_execution(self):
        Clock.unschedule(self.opcode_processor)
        print("Called Pause")
    
    
    def increase_speed(self, speed, max):
        if speed < max:
            Clock.unschedule(self.opcode_processor)
            speed += self.STEP
            self.ids.pb.value = speed
            Clock.schedule_interval(self.opcode_processor, max-speed)
    
    
    def decrease_speed(self, speed, max):
        if speed:
            Clock.unschedule(self.opcode_processor)
            speed -= self.STEP
            self.ids.pb.value = speed
            Clock.schedule_interval(self.opcode_processor, max-speed)
    
    
    def is_valid_gas_price(self, gas_price):
        if not gas_price.isnumeric():
            self.popup_msg(error = "GAS Price should have numeric value")
        
        
    def select_solidity_compiler(self, version):
        if version.startswith("v0"):
            print("Installed Versions:", solcx.get_installed_solc_versions())
            #input("Check")
            if version not in solcx.get_installed_solc_versions():
                self.ids.opcode_comment_text.text = "Wait a while downloading Solidity compiler"
                
                try:
                    solcx.install_solc(version)
                except Exception:
                    msg = "Connection Error\nCheck Internet Connection or \nSelect available version from "+ str(solcx.get_installed_solc_versions())
                    self.popup_msg("Error while downloading required Solidity compiler", reset=0)
                    self.ids.opcode_comment_text.background_color=(1,0,0, .7)
                    self.ids.opcode_comment_text.text = msg
                    return None
            solcx.set_solc_version(version)
            return version
        
        else:
            self.popup_msg(error = "Select Compiler Version", reset = 0) #Execution must continue
            return None
            
             
    def compile_code(self, source_code, version):        
        if self.select_solidity_compiler(version):
            success = True
            try:
                self.compile_solidity_source_code(source_code)
                self.manage_widget(self.ids.sv_options, False)
                msg = "FILE COMPILED SUCCESSFULLY"
                color = (0,1,0, .7)
                print("Green")
            
            except Exception as e:
                color = (1,0,0, .7)
                msg = e.stderr_data
                msg = "No Contract in source" if msg.strip() == "" else msg 
                success = False
            
            self.ids.opcode_comment_text.text = msg
            self.ids.opcode_comment_text.background_color=color
            self.ids.opcode_comment_text.color=(0,0,0, 1)
            
            if success:
                ast_to_cfg_obj = ASTToCFGObject(source_code, self.sc_manager.helper.get_ast(), True)
                self.__cfg_object = ast_to_cfg_obj.get_cfg_object()
                self.opt_module = OPTModule(self.get_cfg_object())
                
                print("Unreachable Nodes:::::::XYZ:::::")
                      
                self.ids.cfg_img_widget.source = "cfg/cfg_src.png"
                self.ids.cfg_img_widget.size =  self.ids.cfg_img_widget.texture_size
                self.ids.cfg_img_widget.reload()
            
              
    def reset_current(self):
        self.__index = -1
        self.instr_counter = 0
        self.opcode_comment.text = "Displays Comments"
        self.compiled_output.text = "Opcode"
        if self.__is_gui:
            if self.__transaction and not self.__transaction.get_contract_addr():
                self.sol_source_code.text = "Source Code"
            self.opcodes_list.adapter.data=[]
            self.stack_list.adapter.data=[]
            self.memory_list.adapter.data=[]
            self.storage_list.adapter.data = []
            self.stack_list._trigger_reset_populate()
            self.memory_list._trigger_reset_populate()
            self.opcodes_list._trigger_reset_populate()
            self.storage_list._trigger_reset_populate()
            self.ids.pb.value = 1 
            self.ids.mn_g.text = " - "
            self.ids.me_g.text = " - "
    
    
    def reload_accounts(self):
        self.__analyze_evm_state()
        self.ids.call_btn.disabled = True
        self.ids.deploy_btn.disabled = True
        self.ids.cont_acc.text = "Select Contract"
        self.ids.cont_acc.values = list(self.__esm.get_contract_accounts())
        self.ids.usr_acc.text = "Select Account"
        self.ids.usr_acc.values = list(self.__esm.get_user_accounts())
        self.ids.gaslimit.text = "0"        
    
    """ Need m,odifications...... take care of text and sm"""
    def analyze_live_variable(self, sm):
        self.get_cfg_builder().perform_live_variable_analysis()
        
        
    def analyze_available_expressions(self, sm):
        self.get_cfg_builder().available_expression_analysis()
         
            
    def analyze_reaching_definitions(self, sm):
        self.get_cfg_builder().reaching_definitions_analysis()
    
    
    def analyze_very_busy_expressions(self, sm):
        self.get_cfg_builder().very_busy_expressions_analysis()
        
        
    def remove_code(self, text, sm):        
        self.manage_widget(self.ids.sv_anlz_vz, False, text); 
        self.ids.sm.current = sm
        self.ids.urc_label = text + " Optimization"
        source_code = self.sol_source_code.text
        index = 0;
        self.sol_source_code.multiselect = True
        self.sol_source_code.selection_color = (1,0,0,0.5)
        fr_to_list = None
        
        #input("Waiting...")
        if text == "Unreachable Code":
            #fr_to_list = self.get_cfg_builder().get_unreachable_src() 
            fr_to_list = self.opt_module.get_unreachable_code()
        elif text == "Dead Code":
            fr_to_list = self.opt_module.get_dead_src() 
        
        print(source_code)
        
        if fr_to_list and text in ["Unreachable Code","Dead Code"]:
            for fr, to in fr_to_list:
                start = fr+index
                end = fr+to+1+index
                comment_text = source_code[start:end]
                print(comment_text,"\n+++")
                source_code=source_code[:start]+"/* "+comment_text + " // "+text +" */" + source_code[end:]
                index+=10+len(text)
        
        elif text == "Optimized Code":
            
            source_code = self.opt_module.get_optimized_code(source_code)
            
        elif text == "Optimized Code Using BS":
            source_code = self.opt_module.get_optimized_code(source_code, True)
            
        self.ids.urc_source_code.text = source_code
        
            
    def get_req_gas(self):
        data = self.stack_list.adapter.data if self.__is_gui else self.__ng_stack_list
        ml = len(self.memory_list.adapter.data if self.__is_gui else self.__ng_memory_list)//2
        
        def Ccall():
            return Cgas_cap() + Cextra()        
    
    
        def Ccall_gas():
            return Cgas_cap() + GasUses.get_price("Gcallstipend") if int(data[2], 16) != 0 else 0
        
        
        def Cgas_cap():
            if self.__transaction.get_remaining_gas() >= Cextra():
                return min((L(self.__transaction.get_remaining_gas() - Cextra()), int(data[0], 16)))
            else:
                return int(data[0], 16)
            
        
        def Cextra():
            return GasUses.get_price("Gcall") + Cxfer() + Cnew()
        
        
        def Cxfer():
            return GasUses.get_price("Gcallvalue") if int(data[2], 16) != 0 else 0
            
        
        def Cnew():
            if self.__esm.get_account("0x"+data[1][-40:]).is_dead() and int(data[2], 16) != 0:
                return GasUses.get_price("Gnewaccount")
            else:
                return 0
        
        
        def L(n):
            return n - floor(n/64)
        
        
        def memory_expansion(f, rl):
            if rl:
                nl = ceil((f + rl) / 32)
                return ml if ml > nl else nl
            else:
                return ml
            
            
        def Cmem(a):
            print("Check",a,"Cost", GasUses.get_price("Gmemory") * a + ceil(a**2 / 512), sep="\n===\n")
            return GasUses.get_price("Gmemory") * a + floor(a**2 / 512)
        
        
        def get_mem_cost(mnemonic):
            if mnemonic in ["SHA3", "RETURN", "REVERT"]:
                return Cmem(memory_expansion(int(data[0], 16), int(data[1], 16)))
            
            elif mnemonic in ["CALLDATACOPY", "CODECOPY", "RETURNDATACOPY"]:
                return Cmem(memory_expansion(int(data[0], 16), int(data[2], 16)))
            
            elif mnemonic == "EXTCODECOPY":
                return Cmem(memory_expansion(int(data[1], 16), int(data[3], 16)))
        
            elif mnemonic in ["MLOAD", "MSTORE"]:
                return Cmem(max((ml, ceil((int(data[0], 16) + 32)/32))))
            
            elif mnemonic in ["MSTORE8"]:
                return Cmem(max((ml, ceil((int(data[0], 16) + 1)/32))))
            
            elif mnemonic == "CREATE":
                return Cmem(memory_expansion(int(data[1], 16), int(data[2], 16)))
            
            elif mnemonic in ["CALL", "CALLCODE"]:
                return Cmem(memory_expansion(int(data[3], 16), int(data[4], 16)) + memory_expansion(int(data[5], 16), int(data[6], 16)))
                
            elif mnemonic in ["STATICCALL", "DELEGATECALL"]:
                return Cmem(memory_expansion(int(data[2], 16), int(data[3], 16)) + memory_expansion(int(data[4], 16), int(data[5], 16)))
        
        
        def cal_gas(mnemonic):
            gas_required = self.instruction_processor.get_gas_requirment()
            
            if gas_required != "FORMULA":
                return eval(gas_required)
            
            if mnemonic == "SSTORE":
                print("STORAGE INFO:: ", self.contract_information, hex(int(data[0],16)), sep = "\n")
                s_info = self.contract_information.get(hex(int(data[0],16)))
                return GasUses.get_price("Gsset") if int(data[1],16) != 0 and ( 0 if not s_info else int(s_info,16) ) == 0 else GasUses.get_price("Gsreset")
            
            elif mnemonic == "EXP":
                exp_bytes = int(data[0], 16)
                if exp_bytes:
                    return GasUses.get_price("Gexp") + GasUses.get_price("Gexpbyte") * (1 + floor(log(exp_bytes, 256)))
                else:
                    return GasUses.get_price("Gexp")
                
            elif mnemonic in ["CALLDATACOPY", "CODECOPY", "RETURNDATACOPY"]:
                return GasUses.get_price("Gverylow") + GasUses.get_price("Gcopy") * ceil(int(data[2], 16) / 32)
            
            elif mnemonic == "EXTCODECOPY":
                return GasUses.get_price("Gextcode") + GasUses.get_price("Gcopy") * ceil(int(data[2], 16) / 32)
            
            elif mnemonic.startswith("LOG"):
                topics = int(mnemonic[3:])
                return GasUses.get_price("Glog") + GasUses.get_price("Glogdata") * int(data[1], 16) + topics * GasUses.get_price("Glogtopic")
            
            elif mnemonic in ["CALL", "CALLCODE", "DELEGATECALL", "STATICCALL"]:
                return Ccall()
            
            elif mnemonic == "SELFDESTRUCT":
                n = self.__esm.get_account("0x"+data[0][-40:]).is_dead() and self.__transaction.get_contract_account().get_balance()!= 0
                return GasUses.get_price("Gselfdestruct") + GasUses.get_price("Gnewaccount") if n else 0
            
            elif mnemonic == "SHA3":
                print(ceil(int(data[1], 16) / 32))
                print("Check::", GasUses.get_price("Gsha3") + GasUses.get_price("Gsha3word") * ceil(int(data[1], 16) / 32))
                return GasUses.get_price("Gsha3") + GasUses.get_price("Gsha3word") * ceil(int(data[1], 16) / 32)

        gas_required = [0]
        mnemonic = self.instruction_processor.get_mnemonic().strip()
        print("mnemonic::", mnemonic)
        gas_required.insert(0,cal_gas(mnemonic))
        
        if(self.instruction_processor.req_mem_exp()):
            gas_required[1] = get_mem_cost(mnemonic)  - Cmem(ml)
            print("Tem Mem Req. Check", gas_required)
        #gr = cal_gas(mnemonic)
        #print("Recheck::: ", gr)
        #gas_required += gr
        #print("INST Gas Req:", gas_required)
        return gas_required
        #
    
    def __get_byte_code_list(self, byte_code):
        return [byte_code[i:i+2] for i in range(0, len(byte_code), 2)]
    
    
    def generate_byte_list_code(self, byte_code):
        if type(byte_code) == str:
            byte_code = self.__get_byte_code_list(byte_code)
        elif type(byte_code) == list:
            byte_code = self.__get_byte_code_list(self.get_code_from_list(byte_code))
        else:
            raise Exception("INVALID INPUT TYPE")
        return byte_code   
    
    
    def get_code_from_list(self, byte_code, start = 0, size = None):
        str_bytes = ""
        
        if size:
            size=(start+size)*2
            
        for data in byte_code:
            str_bytes+=data.split(":")[1].strip()
        return str_bytes[start*2:size]    
        
            
    def get_byte_list_code_with_address(self, start, end = None, evm = 0, byte_code = None, loc = 0):
        byte_code = self.generate_byte_list_code(byte_code)    
        byte_code = byte_code[start:end]    
            
        if evm:
            length = ceil(len(byte_code)/16)
            return["0x{:04x} : {:32s}".format((index+loc)*16, ''.join(byte_code[index*16:(index*16)+16])) for index in range(length)]
        else:
            return ["0x{:04x} : {:2s}".format(index, value) for index, value in enumerate(byte_code)]
            
   
    def update_evm_memory_view(self, location, length):
        return ["0x{:04x} : {:032x}".format((index+length)*16, 0) for index in range(location-length+1)]
    
    
        
class SmartContractExecutionVisualizerApp(App):
    
    def run(self):
#         Config.set('graphics', 'window_state', 'maximized')
#         Config.set('graphics', 'kivy_clock', 'free_all')
#         Config.set('graphics', 'maxfps', 40)
#         Config.set('graphics', 'multisamples', '0')
        Config.write()
        return App.run(self)
    
    
    def __init__(self):
        super(SmartContractExecutionVisualizerApp, self).__init__()
        
    
Factory.register('Root', cls=GUI)
Factory.register('SelectDialog', cls=SelectDialog)


if __name__ == '__main__':
    SmartContractExecutionVisualizerApp().run()