The code is created to experiment the size of an explanation by forgetting and can be run in three ways.

`python myProgram.py J` Creates justifications. Uses the ontology in the inputOntology variable in `myProgram.py`. It searches for the subset statements and creates justifications which can be analysed.

`python myProgram.py F` Runs the forgetting algorithm and prints how many axioms are in the explanation. It uses the justification in `forgetting/justification.omn` and the subclass statement in `forgetting/subclass.nl`.

`python myProgram.py ALL` Runs the whole experiment with the ontology in the inputOntology variable in `myProgram.py`. It uses all justifications of the ontology and runs the forgetting algorithm on it. The results are printed in results.txt. 