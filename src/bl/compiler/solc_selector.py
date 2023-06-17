'''
Created on May 22, 2022

@author: ACER
'''
import solcx
import operator
import re

class SolcSelector(object):
    operator_map = {
    '<': operator.lt,
    '<=': operator.le,
    '>=': operator.ge,
    '>': operator.gt,
    '^': operator.ge
    }
    solidity_versions = ['v0.8.14','v0.8.13','v0.8.12','v0.8.11','v0.8.10','v0.8.9','v0.8.8','v0.8.7','v0.8.6','v0.8.5','v0.8.4','v0.8.3','v0.8.2','v0.8.1','v0.8.0','v0.7.6','v0.7.5','v0.7.4','v0.7.3','v0.7.2','v0.7.1','v0.7.0','v0.6.12','v0.6.11','v0.6.10','v0.6.9','v0.6.8','v0.6.7','v0.6.6','v0.6.5','v0.6.4','v0.6.3','v0.6.2','v0.6.1','v0.6.0','v0.5.17','v0.5.16','v0.5.15','v0.5.14','v0.5.13','v0.5.12','v0.5.11','v0.5.10','v0.5.9','v0.5.8','v0.5.7','v0.5.6','v0.5.5','v0.5.4','v0.5.3','v0.5.2','v0.5.1','v0.5.0','v0.4.26','v0.4.25','v0.4.24','v0.4.23','v0.4.22','v0.4.21','v0.4.20','v0.4.19','v0.4.18','v0.4.17','v0.4.16','v0.4.15','v0.4.14','v0.4.13','v0.4.12','v0.4.11']

    def __init__(self, pragma_str):
        pass
    
    def install_solc_pragma_solc(self, version, install=True):
        version = version.strip()
        comparator_set_range = [i.strip() for i in version.split('||')]
        comparator_regex = re.compile(r'(?P<operator>([<>]?=?|\^))(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))')
        #versions_json = requests.get(ALL_RELEASES).json()
        range_flag = False
        #print("All:", versions_json,"\n",version)
        print(comparator_set_range)
        for version_json in SolcSelector.solidity_versions:
            for comparator_set in comparator_set_range:
                comparators = [m.groupdict() for m in comparator_regex.finditer(comparator_set)]
                comparator_set_flag = True
                for comparator in comparators:
                    operator = comparator['operator']
                    if not SolcSelector._compare_versions(version_json, comparator['version'], operator):
                        comparator_set_flag = False
                if comparator_set_flag:
                    range_flag = True
            if range_flag:
                SolcSelector._check_version(version_json)
                if install:
                    solcx.install_solc(version_json)
                return version_json
        raise ValueError("Compatible solc version does not exist")
    
    @classmethod
    def _check_version(cls, version):
        version = "v0." + version.lstrip("v0.")
        if version.count('.') != 2:
            raise ValueError("Invalid solc version '{}' - must be in the format v0.x.x".format(version))
        v = [int(i) for i in version[1:].split('.')]
        if v[1] < 4 or (v[1] == 4 and v[2] < 11):
            raise ValueError("py-solc-x does not support solc versions <0.4.11")
        return version
    
    @classmethod
    def _compare_versions(cls, v1, v2, comp='='):
        v1 = v1.lstrip('v')
        v2 = v2.lstrip('v')
        v1_split = [int(i) for i in v1.split('.')]
        v2_split = [int(i) for i in v2.split('.')]
        if comp in ('=', '==', '', None):
            return v1_split == v2_split
        if comp not in SolcSelector.operator_map:
            raise ValueError("operator {} not supported".format(comp))
        idx = next((i for i in range(3) if v1_split[i] != v2_split[i]), 2)
        if comp == '^' and idx != 2:
            return False
        return SolcSelector.operator_map[comp](v1_split[idx], v2_split[idx])   