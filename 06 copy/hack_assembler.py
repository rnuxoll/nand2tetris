# -*- coding: utf-8 -*-

import sys
import copy

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

# todo one way to get rid of global keywords is to pass global variables as arguments to sub-functions

"""
clean up whitespace and comments
args
    lines: a list containing the original code, including whitespace and comments
returns
    the code without any whitespace or comments
"""
def clean_code(program):
    lines = []
    for line in program:
        if "\xe2" in line:
            line = repr(line)


        # remove whitespace
        line = line.replace(" ", "")
        line = line.strip()  # this will remove newline escape characters

        # ignore comments
        comment_start_index = line.find("//")

        if comment_start_index != -1:
            line = line[:comment_start_index]
        if line == "":  # if the entire line is a comment
            continue
        lines.append(line)

    return lines




"""
processes label symbols
returns
    label_dict: a list containing all the assembly code lines in the program as strings 
modifies
    program: modifies the argument program by removing all of the label symbols
"""
def process_label_symbols(program):
    label_dict = {}

    for n, l in enumerate(program):
        if l[0] == "(" and l[-1] == ")":
            symbol_name = l[1:-1]
            label_dict[symbol_name] = n - len(label_dict)

    for k in label_dict.keys():
        program.remove("("+k+")")

    return label_dict


"""
removes whitespace from the instruction and translates it into its fields

this must search a instructions first in order to define a
"""
def parser(program, label_reference):

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

    global variable_symbols
    variable_symbols = {} # dictionary mapping variable symbols

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
        global variable_symbols
        my_sym = my_sym.strip() # todo this line should be unnecessary
        # first determine if the symbol is variable or pre-defined

        is_label_symbol = False

        address = None
        # if it is a predefined symbol in the hack assembly language
        if my_sym in predefined_symbols.keys():
            address = predefined_symbols[my_sym]
        elif my_sym in label_reference.keys():
            address = label_reference[my_sym]
        # if it is a variable symbols that have already been assigned addresses
        elif my_sym in variable_symbols.keys():
            address = variable_symbols[my_sym]
        elif not is_label_symbol: # if it is a variable symbol that needs to be assigned a
            global last_allocated_memory
            address = last_allocated_memory
            variable_symbols[my_sym] = last_allocated_memory

            last_allocated_memory += 1
            # todo we are reallocating new memory addresses for symbols that have already been allocated
        else:
            raise Exception

        return address

    # define fields, msb
    # if i set a variable
    instructions = []

    for i, line in enumerate(program):
        fields = dict()

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
    assembly_filepath = sys.argv[1]
    output_filepath = sys.argv[2]

    # read and clean assembly code
    assembly_file = open(assembly_filepath, "r")
    assembly_lines = assembly_file.readlines()
    assembly_file.close()
    clean_assembly = clean_code(assembly_lines)

    # read and clean answer key code
    # answer_file = open(answer_key_filepath, "r")
    # dirty_key = answer_file.readlines()
    # answer_file.close()
    # clean_key = clean_code(dirty_key)

    symbols_reference = process_label_symbols(clean_assembly)

    instructions_and_their_fields = parser(clean_assembly, symbols_reference)
    machine_language = code(instructions_and_their_fields)

    with open(output_filepath, "w") as f:
        for line in machine_language:
            f.write(line)
            f.write("\n")


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
