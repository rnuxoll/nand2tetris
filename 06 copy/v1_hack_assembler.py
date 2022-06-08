# -*- coding: utf-8 -*-

import sys
import copy

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

"""
removes whitespace from the instruction and translates it into its fields

this must search a instructions first in order to define a
"""
def parser(program):

    # define all pre-defined symbols and their corresponding values
    predefined_symbols = {"R{0}".format(i):i for i in range(16)}
    predefined_symbols["SP"] = 0
    predefined_symbols["LCL"] = 1
    predefined_symbols["ARG"] = 2
    predefined_symbols["THIS"] = 3
    predefined_symbols["THAT"] = 4
    predefined_symbols["SCREEN"] = 16384
    predefined_symbols["KBD"] = 24576

    global last_allocated_memory
    last_allocated_memory = 16
    global n_labels
    n_labels = 0  # this should not be reset to zero everytime this function is called

    """
    uses built-in methods to turn an integer number into a binary string
    also represents in in 
    """
    def decimal_to_binary(n):
        n = bin(n).replace("0b", "")

        # todo this will overflow for values that are more than 15 bits
        n = "0" * (15 - len(n) ) + n
        if len(n) != 15:
            raise OverflowError("value in assembly code is greater than 2^number of bits - 1")
        return n

    # takes in symbol, returns address
    def map_symbol_to_address(my_sym):
        global n_labels
        my_sym = my_sym.strip()
        # first determine if the symbol is variable or pre-defined

        is_label_symbol = False
        label_address = -1
        is_predefined = my_sym in predefined_symbols.keys()

        if not is_predefined: # check if label by
            # checking if future lines cont ain that substring, and if so, use that to define the memory

            # todo this is redundant since we have a similar loop used again later
            # todo combine the functionality of the two loops into a single loop in order to
            # todo make running the code quicker
            for i, line in enumerate(program):
                if line == "(" + my_sym + ")":
                    is_label_symbol = True
                    i -= 1 # don't count label symbols as lines
                    label_address = i # bind address to the address of the next instruction in the program

        address = None
        if is_predefined:
            address = predefined_symbols[my_sym]
        elif not is_label_symbol:
            global last_allocated_memory
            address = last_allocated_memory
            last_allocated_memory += 1
        else: # catches if it is a label symbol
            global n_labels
            n_labels += 1
            for i, line in enumerate(program):
                if line == "(" + my_sym + ")": # if we find our symbol
                    address = i + 1 - n_labels # bind address to the address of the next instruction in the program

        return address

    # define fields, msb
    # if i set a variable
    instructions = []

    n_empty_line = 0
    for i, line in enumerate(program):
        fields = dict()
        # skip lines that are just whitespace
        if(len(line)) == 0:
            n_empty_line += 1
            continue
        elif ("(" in line and ")" in line):
            n_empty_line += 1
            continue
        else:
            fields["line#"] = i + 1 - n_empty_line

        if line[0] == "@":
            fields["instruction"] = "a"
            fields["original"] = line

            if line[1:].isdigit():
                fields["value"] = decimal_to_binary(int(line[1:]))
            else:
                # this will trigger for symbols (both variable, label and pre-defined)
                address = map_symbol_to_address(line[1:])
                fields["value"] = decimal_to_binary(address)
        else:
            fields["instruction"] = "c"

            index_equals_sign = line.find("=")
            index_semicolon = line.find(";")

            # if there is no semicolon, set the semicolon index to the length of the string
            # so the code still selects the comp field as everything after the equals sign
            if index_semicolon == -1:
                index_semicolon = len(line)

            dest = line[:index_equals_sign]
            # handle no equal signs
            if index_equals_sign == -1:
                dest = ""

            comp = line[index_equals_sign+1:index_semicolon]
            # the jump bits will not throw an error, because an out of bounds index
            # followed by a slice operator in python returns an empty string, whereas
            # a mere out of bounds index without the slice operator does not
            jump = line[index_semicolon+1:]

            # this line alphabetizes the dest field, e.g. so "MD" gets turned into "DM"
            dest = "".join(sorted(dest))

            fields["dest"] = dest
            fields["comp"] = comp
            fields["jump"] = jump

        instructions.append(fields)

    return instructions

"""
translates each field into its corresponding binary value
"""
def code(instructions):
    # fields["a"] = line[3]
    # fields["c"] = line[4:10]
    # fields["d"] = line[11:14]
    # fields["j"] = line[15:18]
    # print(fields)

    # I'm pretty sure hard-coding in these dictionaries is faster
    # than doing string logic. there's also no obvious way to go from
    # comp to c-bits with if statements

    comp_mapping = {
        "0":"0101010",
        "1":"0111111",
        "-1":"0111010",
        "D":"0001100",
        "A":"0110000",
        "M":"1110000",
        "!D":"0001101",
        "!A":"0110001",
        "!M":"1110001",
        "-D":"0001111",
        "-A":"0110011",
        "-M":"1110011",
        "D+1":"0011111",
        "A+1":"0110111",
        "M+1":"1110111",
        "D-1":"0001110",
        "A-1":"0110010",
        "M-1":"1110010",
        "D+A":"0000010",
        "D+M":"1000010",
        "D-A":"0010011",
        "D-M":"1010011",
        "A-D":"0000111",
        "M-D":"1000111",
        "D&A":"0000000",
        "D&M":"1000000",
        "D|A":"0010101",
        "D|M":"1010101"
    }
    dest_mapping = {
        "":"000",
        "M":"001",
        "D":"010",
        "DM":"011",
        "A":"100",
        "AM":"101",
        "AD":"110",
        "ADM":"111"
    }
    jump_mapping = {
        "":"000",
        "JGT":"001",
        "JEQ":"010",
        "JGE":"011",
        "JLT":"100",
        "JNE":"101",
        "JLE":"110",
        "JMP":"111"
    }

    bits = ""
    machine_language = []

    for fields in instructions:
        if fields["instruction"] == "a":
            bits = "0" + fields["value"]
        else:
            bits = "111"

            bits += comp_mapping[fields["comp"]] # add comp bits
            bits += dest_mapping[fields["dest"]] # add dest bits
            bits += jump_mapping[fields["jump"]] # add jump bits

        machine_language.append(bits)

    return machine_language


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    filepath = sys.argv[0]
    filepath = "rect/Rect"
    assembly_filepath = filepath + ".asm"
    answer_key_filepath = filepath + ".hack"

    lines = []
    with open(assembly_filepath) as f:
        for i, line in enumerate(f):
            if "\xe2" in line:
                line = repr(line)

            # remove whitespace
            line = line.replace(" ", "")
            line = line.strip()  # this will remove newline escape characters

            # ignore comments
            comment_start_index = line.find("//")
            if comment_start_index != -1:
                line = line[:comment_start_index]
            if line == "": # if the entire line is a comment
                continue
            lines.append(line)

    instructions_and_their_fields = parser(lines)
    machine_language = code(instructions_and_their_fields)

    answer_file = open(answer_key_filepath, "r")
    answer_key = answer_file.readlines()

    for i in range(len(answer_key)):
        answer_key[i] = answer_key[i].strip()

    for i in range(len(answer_key)):

        # if instructions_and_their_fields[i]["original"] == "@INFINITE_LOOP":
        #     print("the extraneous i is {0}".format(i))


        if answer_key[i] != machine_language[i]:
            print(instructions_and_their_fields[i])
            print("key: {0}".format(answer_key[i]))
            print("me : {0}".format(machine_language[i]))
            print()
        pass

    print(answer_key == machine_language)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
