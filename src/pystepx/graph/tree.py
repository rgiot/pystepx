#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Display tree by using graphviz.
"""

# AUTHOR Romain Giot <romain.giot@ensicaen.fr>

try:
    import pygraphviz as pgv
except:
    pass

from types import ListType


class DrawTree(object):
    """Tree drawer."""

    def __init__(self, tree, name, ftype):
        """Set the tree to draw.
        
        @param tree: Tree to represent
        @param name: name of the file to build
        @param ftype: extension of the file
        """
        self.__tree__ = tree
        self.__name__ = name
        self.__ftype__ = ftype
        self.__indice__ = 0


    def _new_indice(self):
        self.__indice__ += 1
        return self.__indice__

    def draw(self):
        """Draw the tree"""
        tree = self.__tree__
        name = self.__name__

        G = pgv.AGraph(directed=True)
     # G.node_attr.update(color='red')
     # G.edge_attr.update(len='2.0',color='blue')


        self.draw_rec(tree, G, 1)
        G.draw('%s.%s' % (name, self.__ftype__) , self.__ftype__, 'dot')
        return G

    def draw_rec(self, tree, G, level):
      if len(tree) == 0: return G


      indice = self._new_indice()

      if not isinstance(tree, ListType):
        node = tree
        self.add_node(node, indice, G)
        return indice

      else:
        indices = []
        node = tree[0]
        tree = tree[1:]
        
        self.add_node(node, indice, G)

        #loop all over children
        for i in range(node[1]):
          indices.append(self.draw_rec(tree[i], G, level+1))

        for i in range(len(indices)):
          G.add_edge(indice, indices[i])

        return indice

    def add_node(self, node, indice, G):
      """Add a node to the graph
      @param node : tuple to add
      @param G : graph
      @param indice: id of the node
      """

      if    node[0] == 3 : #input
        G.add_node( indice, label=node[2], shape='circle' )
      elif  node[0] == 4 : #const
        G.add_node( indice, label=node[2],shape='octagon' )
      elif  node[0] == 0 : #root
        G.add_node( indice, label=node[2], shape='diamond' )
      else:
        G.add_node( indice, label=node[2], shape='rect' )



