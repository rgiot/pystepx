.. sectionauthor: Romain giot <romain.giot@ensicaen.fr>

How trees are stored ?
======================

Presentation
------------

In this part, we will see how trees are stored in the library.
This would be usefull when building trees at hand or creating 
new interpreation routs which sit for a particular problem.

The trees are stored in nested arrays which allows to work them
with recursive methods and is a simple structure.
The following tree (1+(x/y)):


.. graphviz::

  digraph tree1 {
    "root" -> "+";
    "+" -> "1";
    "+" -> "/";
    "/" -> "x";
    "/" -> "y";
  }


would (schematically) be stored in the following way:

.. code-block:: python

  [ root, [+, [1, [/, x, y]]]]

Sadly, it is not so simple, the nodes are stored in a particular way.


Tree node
---------

Each node is stored in a tuple at 3 dimensions.

.. code-block:: python

 (NODE_TYPE, NB_CHILDREN, NODE_NAME)

With this representation, when reading a node, we dispose of all the required information with
the need of lookup tables are similar things which could slow down the tree evaluation.

`NODE_TYPE` represents the type of the node. During the evaluation of the tree, the actions can be
different depending on the type. Each node type is represented by an integer.

  * ROOT_BRANCH = 0
  * FUNCTION_BRANCH = 1
  * ADF_DEFINING_BRANCH = 2
  * VARIABLE_LEAF = 3
  * CONSTANT_LEAF = 4
  * ADF_LEAF = 5

  * KOZA_ADF_DEFINING_BRANCH = 6
  * KOZA_ADF_FUNCTION_BRANCH = 7
  * KOZA_ADF_PARAMETER = 8


`NB_CHILDREN` gives the number of children of the node.
This is not a redundant information (it can be obtained from the size of the second
member of the array) because the nodes are used both in the tree (as explained here) and
in the grammar definition (where the information will be used in order to build the tree
according to this grammar).

Common nodes
~~~~~~~~~~~~
In pystep, the first node is always the `ROOT_BRANCH` node. It symbolize the end of the tree.
`FUNCTION_BRANCH` represents a function to execute. The parameters of the functions are the children of
the node. The `VARIABLE_LEAF` leaf represents a variable of the tree to evaluate. The content of the variable
is defined during the configuration of the system. 
The `CONSTANT_LEAF` represents a constant value which is randomly defined during the initialization of the parameters.

The following tree:

.. code-block:: python

  [(0, 1, 'root'), [(1, 2, '-'), [(1, 1, '^2'), [(1, 2, '-'), (3, 0, 'x'), (3, 0, 'x')]], [(1, 1, 'neg'), [(1, 2, '*'), (3, 0, 'x'), (3, 0, 'x')]]]]


will give:

.. graphviz::

  strict digraph {
        node [label="\N"];
        1        [label=root,
                shape=diamond];
        2        [label="-",
                shape=rect];
        1 -> 2;
        7        [label=neg,
                shape=rect];
        2 -> 7;
        3        [label="^2",
                shape=rect];
        2 -> 3;
        4        [label="-",
                shape=rect];
        3 -> 4;
        6        [label=x,
                shape=circle];
        4 -> 6;
        5        [label=x,
                shape=circle];
        4 -> 5;
        8        [label="*",
                shape=rect];
        7 -> 8;
        9        [label=x,
                shape=circle];
        8 -> 9;
        10       [label=x,
                shape=circle];
        8 -> 10;
  }

Simple ADF
~~~~~~~~~~
It is possible to create simples ADF: the ADF branch is evaluated one time and compute a value which is stored.
The result can be called in the main program several times with the required type of leaf node.
`ADF_DEFINING_BRANCH` represents the definition of an ADF branch (this is not strictly the same thing than
in the Kooza ADF). This branch must be in the first children of the `ROOT_BRANCH`.
The children of the node represents the function which will be evaluated one time and the result stored.
`ADF_LEAF` represents a leaf node which value have been computed thanks to the ADF branch of the same name.


The following tree:

.. code-block:: python

 [(0, 2, 'root'), [(2, 1, 'adf1'), [(1, 2, '+'), [(1, 2, '*'), [(1, 2, '*'), (3, 0, 'x'), (3, 0, 'x')], [(1, 2, '+'), (3, 0, 'x'), (3, 0, 'x')]], [(1, 2, '+'), [(1, 2, '+'), (3, 0, 'y'), (3, 0, 'x')], [(1, 2, '+'), (3, 0, 'x'), (3, 0, 'y')]]]], [(2, 1, 'adf2'), [(1, 2, 'adf2_+'), [(1, 2, 'adf2_*'), [(1, 2, 'adf2_+'), (5, 0, 'adf1'), (3, 0, 'y')], [(1, 2, 'adf2_*'), (5, 0, 'adf1'), (3, 0, 'y')]], [(1, 2, 'adf2_*'), [(1, 2, 'adf2_+'), (5, 0, 'adf1'), (3, 0, 'y')], [(1, 2, 'adf2_+'), (3, 0, 'y'), (3, 0, 'y')]]]]]


gives:

.. graphviz::

 strict digraph {
	node [label="\N"];
	1	 [label=root,
		shape=diamond];
	2	 [label=adf1,
		shape=rect];
	1 -> 2;
	18	 [label=adf2,
		shape=rect];
	1 -> 18;
	3	 [label="+",
		shape=rect];
	2 -> 3;
	11	 [label="+",
		shape=rect];
	3 -> 11;
	4	 [label="*",
		shape=rect];
	3 -> 4;
	5	 [label="*",
		shape=rect];
	4 -> 5;
	8	 [label="+",
		shape=rect];
	4 -> 8;
	6	 [label=x,
		shape=circle];
	5 -> 6;
	7	 [label=x,
		shape=circle];
	5 -> 7;
	10	 [label=x,
		shape=circle];
	8 -> 10;
	9	 [label=x,
		shape=circle];
	8 -> 9;
	15	 [label="+",
		shape=rect];
	11 -> 15;
	12	 [label="+",
		shape=rect];
	11 -> 12;
	13	 [label=y,
		shape=circle];
	12 -> 13;
	14	 [label=x,
		shape=circle];
	12 -> 14;
	17	 [label=y,
		shape=circle];
	15 -> 17;
	16	 [label=x,
		shape=circle];
	15 -> 16;
	19	 [label="adf2_+",
		shape=rect];
	18 -> 19;
	20	 [label="adf2_*",
		shape=rect];
	19 -> 20;
	27	 [label="adf2_*",
		shape=rect];
	19 -> 27;
	24	 [label="adf2_*",
		shape=rect];
	20 -> 24;
	21	 [label="adf2_+",
		shape=rect];
	20 -> 21;
	23	 [label=y,
		shape=circle];
	21 -> 23;
	22	 [label=adf1,
		shape=rect];
	21 -> 22;
	26	 [label=y,
		shape=circle];
	24 -> 26;
	25	 [label=adf1,
		shape=rect];
	24 -> 25;
	31	 [label="adf2_+",
		shape=rect];
	27 -> 31;
	28	 [label="adf2_+",
		shape=rect];
	27 -> 28;
	29	 [label=adf1,
		shape=rect];
	28 -> 29;
	30	 [label=y,
		shape=circle];
	28 -> 30;
	33	 [label=y,
		shape=circle];
	31 -> 33;
	32	 [label=y,
		shape=circle];
	31 -> 32;
 }


adf1 is first evaluated and its results is stored. The main program is in adf2 which also uses the result of the evaluation of adf1.

This could be seen as:

>>> def adf1(x,y):
...     return ((y+x) + (y +x)) + ((x*x) * (x+x))
... 
>>> def adf2(x,y):
...     _adf1 =adf1(x,y)
...     _adf2 = ((y*_adf1) * (y + _adf1)) + ((y+y) * (_adf1+y))
...     return _adf1, _adf2
... 

Kooza ADF
~~~~~~~~~
We also can use Kooza ADF. The function are first defined, then they can be called in the main program (or in another ADF)
with different parameters each time. The aim of `KOZA_ADF_DEFINING_BRANCH` is to define an ADF branch. 
It must be in the first children of the root node. To call an ADF in the main program, we have to use the
`KOZA_ADF_FUNCTION_BRANCH`, its children are the parameters of the defined function (which are represented by `KOZA_ADF_PARAMETER`).


The tree:

>>> tree = [(0, 2, 'root'), [(6, 1, 'ADF0'), [(1, 2, 'ADF0_+'), (8, 0, 'ADF0_PARAM0'), (8, 0, 'ADF0_PARAM1')]], [(0, 2, '_root'), [(7, 2, '_ADF0'), (3, 0, 'x'), (3, 0, 'x')], [(1, 2, '*'), (3, 0, 'x'), (3, 0, 'y')]]]

gives the following representation:

.. graphviz::

 strict digraph {
	node [label="\N"];
	1	 [label=root,
		shape=diamond];
	2	 [label=ADF0,
		shape=rect];
	1 -> 2;
	6	 [label=_root,
		shape=diamond];
	1 -> 6;
	3	 [label="ADF0_+",
		shape=rect];
	2 -> 3;
	4	 [label=ADF0_PARAM0,
		shape=rect];
	3 -> 4;
	5	 [label=ADF0_PARAM1,
		shape=rect];
	3 -> 5;
	7	 [label=_ADF0,
		shape=rect];
	6 -> 7;
	10	 [label="*",
		shape=rect];
	6 -> 10;
	8	 [label=x,
		shape=circle];
	7 -> 8;
	9	 [label=x,
		shape=circle];
	7 -> 9;
	11	 [label=x,
		shape=circle];
	10 -> 11;
	12	 [label=y,
		shape=circle];
	10 -> 12;
 }


In this example, we defined one ADF. This generated ADF has two different parameters which are added together.
The main program (`_root` node) use this automatically defined ADF and gives its parameters.
This could be seen as:

>>> def adf0(param0, param1):
...     return param0 + param1
... 
>>> def _root(x,y):
...     return adf0(x, x), x*y
... 

Displaying a tree
-----------------

If needed, you can display a tree.
We have created the class pystepx.graph.tree.DrawTree for this aim.
The procedure is really simple:

>>> tree = [(0, 1, 'root'), [(1, 2, '-'), [(1, 1, '^2'), [(1, 2, '-'), (3, 0, 'x'), (3, 0, 'x')]], [(1, 1, 'neg'), [(1, 2, '*'), (3, 0, 'x'), (3, 0, 'x')]]]]
>>> import pystepx.graph.tree
>>> gt = pystepx.graph.tree.DrawTree(tree, 'test', 'jpg')
>>> gt.draw()
strict digraph {
        node [label="\N"];
        1        [label=root,
                shape=diamond];
        2        [label="-",
                shape=rect];
        1 -> 2;
        .......
        9        [label=x,
                shape=circle];
        8 -> 9;
        10       [label=x,
                shape=circle];
        8 -> 10;
 }


