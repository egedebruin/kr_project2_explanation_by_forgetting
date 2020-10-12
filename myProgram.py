import subprocess
from shutil import copyfile

# Choose the ontology (in the OWL format) for which you want to explain the entailed subsumption relations.
inputOntology = "datasets/pizza.owl"

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


def forget_symbol(symbol):
    global forgetOntology
    global total_axioms
    if symbol in subclass_symbols:
        return

    print("forgetting: " + symbol)
    signature_file = open(signature, "w")
    signature_file.write(symbol)
    signature_file.close()

    lethe_command = 'java -cp lethe-standalone.jar uk.ac.man.cs.lethe.internal.application.ForgettingConsoleApplication --owlFile ' + forgetOntology + ' --method ' + method + ' --signature ' + signature
    subprocess.Popen(lethe_command, shell=True, stdout=subprocess.DEVNULL).wait()

    copyfile('result.owl', tempResultFile)
    forgetOntology = tempResultFile

    axioms = file_to_string(forgetOntology)

    amount_axioms = axioms.count('<rdfs:subClassOf')

    print("Amount axioms: " + str(amount_axioms))
    total_axioms += amount_axioms

#os.system('java -jar kr_functions.jar ' + 'saveAllSubClasses' + " " + inputOntology)

#os.system('java -jar kr_functions.jar ' + 'saveAllExplanations' + " " + inputOntology + " " + inputSubclassStatements)


forget_order = sort_explanation_on_occurrences(forgetOntology)
subclass_symbols = file_to_string(inputSubclassStatements)
total_axioms = 0

print("Start Forget A-Z")
for symbol_tuple in forget_order:
    forget_symbol(symbol_tuple[0])

print("Total amount of axioms: " + str(total_axioms) + "\n")

forgetOntology = "datasets/exp-1.omn"

total_axioms = 0

print("Start Forget Z-A")
for symbol_tuple in reversed(forget_order):
    forget_symbol(symbol_tuple[0])

print("Total amount of axioms: " + str(total_axioms) + "\n")
