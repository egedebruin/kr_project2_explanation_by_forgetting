import subprocess
import sys
import os
import glob
from shutil import copyfile

# Choose the ontology (in the OWL format) for which you want to explain the entailed subsumption relations.
inputOntology = "datasets/cgilith.owl"

# Choose the set of subclass for which you want to find an explanation.
# this file can be generated using the second command (saveAllSubClasses)
inputSubclassStatements = "datasets/subClasses.nt"

# Choose the ontology to which you want to apply forgetting. This can be the inputOntology, but in practise
# should be a smaller ontology, e.g. created as a justification for a subsumption
forgetOntology = "datasets/exp-1.omn"

# Decide on a method for the forgetter (check the papers of LETHE to understand the different options).
# The default is 1, I believe.
# 1 - ALCHTBoxForgetter
# 2 - SHQTBoxForgetter
# 3 - ALCOntologyForgetter
method = "3" #

# Choose the symbols which you want to forget.
signature = "datasets/signature.txt"

tempResultFile = "temp/result_temp"

experimentResultFile = "results.txt"


def forget():
    global forgetOntology

    forget_order = sort_explanation_on_occurrences(forgetOntology)
    subclass_symbols = file_to_string(inputSubclassStatements)
    total_axioms_1 = 0
    copyfile(forgetOntology, tempResultFile)

    start_axioms = sum(1 for line in open(forgetOntology)) - 2
    amount_symbols_to_forget = len(forget_order)
    stdv = calculate_standard_deviation(forget_order)

    print("Start Forget A-Z")
    for symbol_tuple in forget_order:
        new_axioms = forget_symbol(symbol_tuple[0], subclass_symbols)
        if new_axioms == -1:
            continue
        if new_axioms == 0:
            print("Amount of axioms should not be 0, aborting this justification.")
            return
        total_axioms_1 += new_axioms

    print("Total amount of axioms: " + str(total_axioms_1) + "\n")

    copyfile(forgetOntology, tempResultFile)

    total_axioms_2 = 0

    print("Start Forget Z-A")
    for symbol_tuple in reversed(forget_order):
        new_axioms = forget_symbol(symbol_tuple[0], subclass_symbols)
        if new_axioms == -1:
            continue
        if new_axioms == 0:
            print("Amount of axioms should not be 0, aborting this justification.")
            return
        total_axioms_2 += new_axioms

    print("Total amount of axioms: " + str(total_axioms_2) + "\n")

    with open(experimentResultFile, "a") as myfile:
        myfile.write(str(amount_symbols_to_forget) + ", " + str(start_axioms) + ", " + str(stdv) + ", " + str(total_axioms_1) + ", " + str(total_axioms_2) + "\n")


def calculate_standard_deviation(tuples):
    sum = 0
    for symbol_tuple in tuples:
        sum += symbol_tuple[1]

    mean = sum / len(tuples)

    variance_sum = 0
    for symbol_tuple in tuples:
        variance_sum += (symbol_tuple - mean) ** 2
    variance = variance_sum / len(tuples)

    return variance ** 0.5


def sort_explanation_on_occurrences(explanation_file):
    file = open(explanation_file)
    symbol_list = {}
    for line in file:
        if line.startswith("Ontology"):
            continue

        match = ""
        add_character = False
        for character in line:
            if character == '>':
                if match in symbol_list.keys():
                    symbol_list[match] += 1
                else:
                    symbol_list[match] = 1
                add_character = False
                continue
            if character == '<':
                match = ""
                add_character = True
                continue
            if add_character:
                match += character
    result = sorted(symbol_list.items(), key=lambda item: item[1])
    return result


def file_to_string(subclass_file):
    file = open(subclass_file)
    result = ""
    for line in file:
        result += line
    return result


def count_axioms(result_file):
    file = open(result_file)
    result = 0
    for line in file:
        if "<rdfs:subClassOf" in line:
            if "Nothing" not in line:
                result += 1
    return result


def forget_symbol(symbol, subclass_symbols):
    global forgetOntology

    if symbol in subclass_symbols:
        return -1

    print("forgetting: " + symbol)
    signature_file = open(signature, "w")
    signature_file.write(symbol)
    signature_file.close()

    lethe_command = 'java -cp lethe-standalone.jar uk.ac.man.cs.lethe.internal.application.ForgettingConsoleApplication --owlFile ' + tempResultFile + ' --method ' + method + ' --signature ' + signature
    subprocess.Popen(lethe_command, shell=True, stdout=subprocess.DEVNULL).wait()

    copyfile('result.owl', tempResultFile)

    amount_axioms = count_axioms(tempResultFile)

    print("Amount axioms: " + str(amount_axioms))
    return amount_axioms


def copy_subclasses_to_directory():
    files = glob.glob('forgetting/subclasses/*')
    for file in files:
        os.remove(file)

    file = open(inputSubclassStatements)
    i = 0
    for line in file:
        subclass_file = open('forgetting/subclasses/subclass_' + str(i) + ".nt", "w")
        subclass_file.write(line)
        subclass_file.close()
        i += 1


def checkFile(forget_ontology):
    file = open(forget_ontology)
    for line in file:
        if line.startswith("Ontology("):
            continue
        if line.startswith("SubClassOf("):
            continue
        if line.startswith(")"):
            continue
        return True
    return False


if sys.argv[1] == 'F':
    signature = "forgetting/signature.txt"
    forgetOntology = "forgetting/justification.omn"
    inputSubclassStatements = "forgetting/subclass.nt"
    forget()
elif sys.argv[1] == 'J':
    os.system('java -jar kr_functions.jar ' + 'saveAllSubClasses' + " " + inputOntology)

    os.system('java -jar kr_functions.jar ' + 'saveAllExplanations' + " " + inputOntology + " " + inputSubclassStatements)
elif sys.argv[1] == 'ALL':

    print("Calculating subclasses")
    command = 'java -jar kr_functions.jar ' + 'saveAllSubClasses' + " " + inputOntology
    subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL).wait()
    print("Done calculating subclasses")

    copy_subclasses_to_directory()

    files = glob.glob('forgetting/subclasses/*')
    signature = "forgetting/signature.txt"
    forgetOntology = "forgetting/justification.omn"
    inputSubclassStatements = "forgetting/subclass.nt"

    with open(experimentResultFile, "w") as myfile:
        myfile.write("symbols_to_forget, start_axioms, stdv, A-Z, Z-A\n")

    for file in files:
        print("Calculating justification")
        command = 'java -jar kr_functions.jar ' + 'saveAllExplanations' + " " + inputOntology + " " + file

        process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL)
        try:
            process.wait(15)
        except:
            print("Process took too long, terminate")
            process.terminate()
            continue

        print("Done calculating justification")
        if checkFile('datasets/exp-1.omn'):
            copyfile(file, inputSubclassStatements)
            copyfile('datasets/exp-1.omn', forgetOntology)
            forget()
