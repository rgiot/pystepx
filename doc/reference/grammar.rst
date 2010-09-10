Grammar definition
==================

Pystep is a strongly typed genetic programming engine. That's why we have to built
a grammar before using it.

How to set Grammar Rules to build trees
---------------------------------------

If you want to build a tree with very detailed and specific grammar rules, you need to know what Pystep expects you to do.

A tree always starts with a Root node at the top. The root node has no specific operator in it, but it is recognised by Pystep as the top of the tree.

You must specify for each parent node what are the possible children nodes. You must specify how many children nodes this parent node can have, and for each child node you must specify a function and a terminal set (if a parent can only have function nodes as children, specify the function set and an empty terminal set)... This looks all a bit confusing at the moment, so let's get through it with simple examples.

Example 1: A tree with simple arithmetic and one result.

.. code-block:: python

        # default function set applicable for nodes:
        defaultFunctionSet= [(1,2,'+'),(1,2,'*'),(1,1,'^2'),(1,2,'-'),(1,1,'cos'),(1,1,'sin'),(1,1,'neg')]
        # default terminal set applicable for nodes:
        defaultTerminalSet= [(3,0,'x')]

        treeRules = {

        # The root node only has one child. This child can be either a function node or a terminal node.
        'root':[(defaultFunctionSet,defaultTerminalSet)],

        # The + node has two children. Each child can be either a function node or a terminal node.
        '+':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],

        # The * node has two children. Each child can be either a function node or a terminal node.
        '*':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],

        # The ^2 node only has one child. This child can be either a function node or a terminal node.
        '^2':[(defaultFunctionSet,defaultTerminalSet)],

        # The - node has two children. Each child can be either a function node or a terminal node.
        '-':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],

        # The neg node only has one child. This child can be either a function of the type +, *, -, cos, and sin or a terminal node.
        'neg':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'cos'),(1,1,'sin')],defaultTerminalSet)],

        # The cos node only has one child. This child can be either a function of the type +, *, -, neg, and sin or a terminal node.
        'cos':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'sin'),(1,1,'neg')],defaultTerminalSet)],

        # The sin node only has one child. This child can be either a function of the type +, *, -, neg, and cos or a terminal node.
        'sin':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'cos'),(1,1,'neg')],defaultTerminalSet)]
        }

 

Example 2: A tree with hybrid systems: mixing discrete and contimuous representation (logic+arithmetic).

.. code-block:: python

        # default function set applicable by for branches:
        defaultFunctionSet= [(1,2,'+'),(1,2,'*'),(1,1,'^2'),(1,2,'-'),(1,1,'cos'),(1,1,'sin'),(1,1,'neg')]
        # default terminal set applicable by for branches:
        defaultTerminalSet= [(3,0,'x'),(3,0,'y')]


        treeRules = {

        # The root node has three children in a specific order. The first child can only be a If function node. The second child can only be a Then function node. The third child can only be a Else function node.

        'root':[([(2,1,'if')],[]),([(2,1,'then')],[]),([(2,1,'else')],[])],

        # The If node has only one child. This child can be only a function node (either and, or, >, <, or =).
        'if':[([(1,2,'and'),(1,2,'or'),(1,2,'>'),(1,2,'<'),(1,2,'=')],[])],

        # The Then node has only one child. This child can be either a default function node or a default terminal node.

        'then':[(defaultFunctionSet,defaultTerminalSet)],

        # The Else node has only one child. This child can be either a default function node or a default terminal node.
        'else':[(defaultFunctionSet,defaultTerminalSet)],

        # The And node has two children. Each child can be only a function node (either and, or, >, <, or =).
        'and':[([(1,2,'and'),(1,2,'or'),(1,2,'>'),(1,2,'<'),(1,2,'=')],[]),([(1,2,'and'),(1,2,'or'),(1,2,'>'),(1,2,'<'),(1,2,'=')],[])],

        # The Or node has two children. Each child can be only a function node (either and, or, >, <, or =).
        'or':[([(1,2,'and'),(1,2,'or'),(1,2,'>'),(1,2,'<'),(1,2,'=')],[]),([(1,2,'and'),(1,2,'or'),(1,2,'>'),(1,2,'<'),(1,2,'=')],[])],

        # The = node has two children. Each child can be either a default function node or a default terminal node.
        '=':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],

        # The > node has two children. Each child can be either a default function node or a default terminal node.
        '>':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],

        # The < node has two children. Each child can be either a default function node or a default terminal node.
        '<':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],

        # The + node has two children. Each child can be either a default function node or a default terminal node.
        '+':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],

        # The * node has two children. Each child can be either a default function node or a default terminal node.
        '*':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],

        # The ^2 node has only one child. This child can be either a default function node or a default terminal node.
        '^2':[(defaultFunctionSet,defaultTerminalSet)],

        # The - node has two children. Each child can be either a default function node or a default terminal node.
        '-':[(defaultFunctionSet,defaultTerminalSet),(defaultFunctionSet,defaultTerminalSet)],

        # The neg node only has one child. This child can be either a function of the type +, *, -, cos, and sin or a default terminal node.
        'neg':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'cos'),(1,1,'sin')],defaultTerminalSet)],

        # The cos node only has one child. This child can be either a function of the type +, *, -, neg, and sin or a default terminal node.
        'cos':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'sin'),(1,1,'neg')],defaultTerminalSet)],

        # The sin node only has one child. This child can be either a function of the type +, *, -, neg, and cos or a default terminal node.
        'sin':[([(1,2,'+'),(1,2,'*'),(1,2,'-'),(1,1,'cos'),(1,1,'neg')],defaultTerminalSet)]
        }

 
Quick Run
---------

To execute the evolution run of the first tutorial, create a main method in Python (there is one main module already made for you in the package if you want...).
Inside, you need to:

  1 import the module called "evolver"
  2 define a name and path for you database.
  3 and then call the EvolutionRun method from the evolver module.
e.g. of a main file:


.. code-block:: python

        import evolver

        if __name__ == "__main__":

            dbname=r'C:\pop_db'
            evolver.EvolutionRun(2000,(0,1,'root'),2,8,'AddHalfNode',100, 0.001 ,0.5,0.49,dbname,True)


This means that we define:

  *   a population size of 2000 individuals,
  *   a root node with 1 child
  *   a minimum tree depth of 2
  *   a maximum tree depth of 8
  *   the use of a Ramped half and Half Koza tree building method
  *   a maximum number of runs of 100 generations before we stop
  *  a stoping fitness criteria of 0.001 (if the fitness<=0.001, solution found)
  *  a crossover probability of 0.5
  *  a mutation probability of 0.49
  *  a reproduction probability of 0.01
  *  a database of name and path dbname
  *  a run done in verbose mode (printing the fittest element of each generation)

The run will create a database file containing tables of names tab0, tab1,... where every table contains the population for the corresponding generation.

For those who want details of the populations, there are methods in the module writepop that allow to:

  - get stats from a database table: GetPopStatFromDB(dbname,tablename)
  - print the population from a database table to a file: PrintPopFromDB(dbname,tablename,filename)

On a more personal note, I enjoyed programming this API using the Eclipse IDE (there is a pyDev module that allows to use Eclipse to program in Python).

It's great and I recommend it !

Feedback and input are highly welcomed :)

Eh ! I have ADFs in my code !
-----------------------------

It is necessary to build specific rules when using trees containing ADF.

Simple ADF
~~~~~~~~~~


Koza ADF
~~~~~~~~

You have to define grammars especially for each ADF.
ATTENTION, you have to respect a strict naming scheme in order to use the ADF:

  * If `NAME` is the name of the node which defines the ADF branch, `_NAME` must be the name of
    the node calling it.
  * When designing the grammar we set the number of potential parameters. These parameters must be named: `NAME_PARAMi`,
    with i the number of the parameter (starting from 0).
