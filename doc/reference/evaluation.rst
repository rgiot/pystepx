Tree evaluation
===============

The trees can be evaluated in two main ways:

 * From leaves to root: all the nodes are evaluated, we execute a node after having executed its children.
   Even the conditional branches which do not met the condition are evaluated. We can see each node as a mathematical function.
   In this case, we want to create a function which fits our needs.
 * From root to leave: we execute one node, and it choose to execute one or all its children node as he want. We can see the internal
   node as a part of reflexion and the leaves as action to execute.
   In this case, we want to create an intelligent program (i.e., a robot which does things).


Another point of variation is the use of ADF or not (simple of Koza ones) etc...


That is why we have several evaluation function which are more adapted for specific problems.
Concerning the root to leave, for the moment, it's up to the function nodes to manage its execution.
