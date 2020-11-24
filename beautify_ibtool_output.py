#!/usr/bin/python

# this file aims to re-arrange the output of the ibtool output
# the original output file has reference number 
# this script aims to eliminate all the reference numbers


import re
import sys

class IBItem(object):
    def __init__(self, name):
        """
        initializing IBitem with name
        """
        self.name = name
        self.key_values = []
        self.reference_index_list = []

    
    def update(self, line):
        '''
            for each encountered line, update IBItem key and value
        '''
        search_result = re.search(EQUATION_MARK, line)
        key_string = search_result.group(1).strip()
        value_string = search_result.group(2)
        self.key_values.append((key_string, value_string))

        if re.match(AT_NUM_MARK, value_string):
            reference_num = get_reference_num(value_string)
            self.reference_index_list.append(reference_num)
            return True
        else:
            return False


    def get_content(self):
        if self.name == 'NSString':
            return 
        return (self.name, self.key_values)

    
    def get_name(self):
        return self.name


    def get_key_values(self):
        return self.key_values

    
    def get_reference_index_list(self):
        return self.reference_index_list
    # def get_content2(self):
    #     if self.name == 'NSString':
    #         return self.key_values[1]
    #     else:

    def print_self(self):
        print(self.get_name())
        for key, value in self.get_key_values():
            print('\t{}: {}'.format(key, value))

    
EQUATION_MARK = re.compile(r'(.*) = (.*)')
# ARE = re.compile(r'(.*) = (.*)')
STARTS_WITH_BEGIN_ITEM = re.compile(r'^begin_item')
AT_NUM_MARK = re.compile('@[0-9]+$')


def get_reference_num(at_str):
    return int(at_str[1:])


def get_initial_ibitem(ibitem_list):
    length = len(ibitem_list)
    is_referred_list = [False for i in range(length)]

    for item in ibitem_list:
        key_value_pair_list = item.get_key_values()
        for key, value in key_value_pair_list:
            # print(value)
            if re.match(AT_NUM_MARK, value):
                reference_num = get_reference_num(value)
                if not is_referred_list[reference_num]:
                    is_referred_list[reference_num] = True

    initial_ibitem_list = []
    for count, item in enumerate(is_referred_list):
        # print(item, count)
        if not item:
            initial_ibitem_list.append(count)

    return initial_ibitem_list


def beautiful_print(ibitem, ibitem_list, avoid_list, level = 0, key_name = ''):
    prefix = ''
    for i in range(level):
       prefix += '\t'

    if ibitem.get_name() == 'NSString':
        print(prefix + key_name+': ' + ibitem.get_key_values()[0][1])
        return
    
    if ibitem.get_name() == 'NSNumber':
        print(prefix + key_name + ': ' + ibitem.get_key_values()[0][1])
        return

    if key_name == '':
        print(prefix + ibitem.get_name())
    else:
        print(prefix + key_name+': '+ibitem.get_name())

    # print('\n')
    for key, value in ibitem.get_key_values():
        # print(prefix + '\t{}: {}'.format(key, value))
        if re.match(AT_NUM_MARK, value):
            reference_num = get_reference_num(value)
            if avoid_list[reference_num]:
                print(prefix+'\t{}: {}'.format(key, value))
            else:
                nested_item = ibitem_list[reference_num]
                beautiful_print(nested_item, ibitem_list, avoid_list, level+1, key)
        else:
            print(prefix+'\t{}: {}'.format(key, value))

    return

    
def beautify_output(initial_ibitem_list, ibitem_list, avoid_list):
    for initial_item_index in initial_ibitem_list:
        initial_item = ibitem_list[initial_item_index]
        beautiful_print(initial_item, ibitem_list, avoid_list)


def detect_circle(IBItem_list):
    in_degree_list = [0 for i in range(len(IBItem_list))]
    out_reach_list = [[] for i in range(len(IBItem_list))]

    for count, item in enumerate(IBItem_list):
        # print(item.get_reference_index_list())
        _reference_index_list = item.get_reference_index_list()
        out_reach_list[count] = _reference_index_list
        for i in _reference_index_list:
            in_degree_list[i] += 1

    # print(in_degree_list)
    # print(out_reach_list)


    def is_there_zero(_list, already_considered_list):
        # print(_list)
        # print(already_considered_list)
        result = None
        for count, item in enumerate(_list):
            # print(count)
            if item == 0:
                if count in already_considered_list:
                    continue
                else:
                    return count
            else:
                continue
        return None


    already_considered_list = []
    zero_index = is_there_zero(in_degree_list, already_considered_list)
    while(zero_index is not None):
        
        already_considered_list.append(zero_index)
        # print(already_considered_list)
        for item in out_reach_list[zero_index]:
            in_degree_list[item] -= 1

        # print(in_degree_list)
        # print(out_reach_list)

        zero_index = is_there_zero(in_degree_list, already_considered_list)
    
    def remove_item(_list, item):
        if item in _list:
            _list.remove(item)
        return _list

    for i in range(len(IBItem_list)):
        for count, index_list in enumerate(out_reach_list):
            if len(index_list) == 0:
                for index_list in out_reach_list:
                    index_list = remove_item(index_list, count)

    safe_list = []
    for count, item in enumerate(out_reach_list):
        if len(item) == 0:
            safe_list.append(count)

    for count, item in enumerate(in_degree_list):
        if item == 0 and item not in safe_list:
            safe_list.append(count)
    
    # print(safe_list)

    return safe_list


def main(file_name):
    f = open(file_name)
    line = f.readline()
    IBItem_list = []
    while(line):
        if re.match(STARTS_WITH_BEGIN_ITEM, line) or re.match(EQUATION_MARK, line):
            if re.match(STARTS_WITH_BEGIN_ITEM, line):
                name = line.split(' ')[-1].strip()
                ibItem = IBItem(name)
                IBItem_list.append(ibItem)
            else:
                # print(line)
                if(IBItem_list[-1].update(line)):
                    new_referenced_index = IBItem_list[-1].get_reference_index_list()[-1]       
            
        line = f.readline()

    f.close()

    # for item in IBItem_list:
    #     print(item.get_content())

    index_list = get_initial_ibitem(IBItem_list)
    

    safe_list = detect_circle(IBItem_list)
    if len(safe_list) == len(IBItem_list):
        print('safe')
    else:
        print('warning: circle')

    avoid_list = [i not in safe_list for i in range(len(IBItem_list))]
    # print(avoid_list)

    beautify_output(index_list, IBItem_list, avoid_list)
    print()
    for count, i in enumerate(avoid_list):
        if i:
            print('@{}'.format(count))
            beautiful_print(IBItem_list[count], IBItem_list, avoid_list)
            
            

def test():
    line = "@12"
    match_result = re.match(AT_NUM_MARK, line)
    print(int(line[1:]))
    print(match_result)


if __name__ == '__main__':
    main(file_name = sys.argv[1])
    # test()
