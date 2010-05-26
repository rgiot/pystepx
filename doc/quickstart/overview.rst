.. sectionauthor: Romain giot <romain.giot@ensicaen.fr>
.. sectionauthor: Mehdi Khoury <mehdi.khoury@gmail.com>

pySTEP - an overview
====================

Introduction
------------

[pySTEP]_ stands for Python Strongly Typed gEnetic Programming.

It is *a light* **Genetic Programming API** that allows the user to easily evolve populations of trees with precise grammatical and structural constraints. In other worlds you can set up building blocks and rules that define individuals during the evolution. 


Why using rules and constraints ?
---------------------------------

.. note::

    Let's take the example of the DNA of a human being which is 95% similar to the DNA of a chimp. This means that there is some strong similarity in the building blocks and the structure of the genetic code. A completely random genetic code would make no sense on a functional practical point of view because it would give some kind of unfit and disfunctional goo... I just think that, to be useful, artificial evolution has to be able to integrate basic rules that determine the shape of the individuals generated, so that we can get practical results. This does not mean we eliminate random search and we still admit poorly fit individuals. But at least we focus the search in the direction of the problem by only generating potentially useful solutions. 


Implemented Features
--------------------

pySTEP is presently functional, running and stable. Still in the process of adding extra tutorials, extra features for reading the populations from the database, and modify some of the crossover code (so far, only 1-point crossover is used).

There has been a lot of improvement going on since the first version:

* Version 3 (which breaks compatibility with version 2):

    * Possibility of compiling the trees in order to speed up their evaluation (usefull, when each tree has to be evaluated several times with different inputs).
    * Implementation of a simple synchronous distributed island model.
    * More object-oriented in order to ease specialization.
    * Suppression of the settings.py and embedding in a real library.
    * Utilisation of [Cython]_ to speed up execution.

* Version 2:

    * The Koza Strongly-Typed flavoured build methods have been simplified and optimized (around 10 times faster for a code length reduced by five!)
    * It is now possible to use a specific function-terminal sets for each of the children node. And these children node are built in the order they appear in the tree constraints (this feature only existed for ADF in the previous version). This makes pySTEP very competitive and gives it a serious advantage over existing Strongly typed GP packages :)
    * It is now possible to specify what happens after the system has tried 100 times to produced rules-compliant offsprings using crossover but has failed (this might happens if we use a lot of constraining rules). Either we accept the unfit offsprings with Substitute_Mutation=0 or we substitute them with a mutated tree by setting Substitute_Mutation=1.
    * The parameters of the tournament selection are integrated in the main function that calls the evolutionary run. 
    * Code for crossover and mutation is now simplified and clearer.


.. [pySTEP] M. Khoury, R. Giot,
  Python Strongly Typed gEnetic Programming, http://pystep.sourceforge.net
.. [Cython] The Cython compiler, http://cython.org
