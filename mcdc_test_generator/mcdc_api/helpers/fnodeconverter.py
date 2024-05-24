from pysmt.shortcuts import serialize

#This method is needed as the solve function returns fnodes which can not be serialized to a json format
def convert_fnode_to_string(result):
    converted_list = []    
    for item in result:
        fnode_str_list = [serialize(fnode) for fnode in item.keys()]
        value_str_list = [serialize(fnode) for fnode in item.values()]
        new_dict = dict(zip(fnode_str_list, value_str_list))
        converted_list.append(new_dict)
    return converted_list