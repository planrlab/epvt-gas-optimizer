'''
Created on २५ जून, २०१९

@author: JH-ANIC
'''

class GasUses(object):
    
    __gas_prices = None
    __file_name = "../../lib/operations.txt"
    
    
    @classmethod
    def load_operation_info(cls):
        if not cls.__gas_prices:
            with open(cls.__file_name, 'r') as inputfile:
                cls.__gas_prices = eval(inputfile.read())
            #print("Hello...", GasUses.__gas_prices)
        
        
    @classmethod
    def update_gas_prices_dict(cls, gas_prices):
        cls.__gas_prices.update(gas_prices)
        
    
    
    @classmethod
    def get_price(cls, mnemonic):
        return cls.__gas_prices.get(mnemonic)
    
    
    @classmethod    
    def get_txdata_gas_uses(cls, tx_data):
        zero = 0
        nonzero = 0
        for k in range(0, len(tx_data), 2):
            if tx_data[k:k+2] == "00":
                zero+=1
            else:
                nonzero+=1
        return sum((zero*cls.__gas_prices.get("Gtxdatazero"), nonzero*cls.__gas_prices.get("Gtxdatanonzero")))
    
    
    def get_req_gas(self, mnemonic):
        pass
    
    