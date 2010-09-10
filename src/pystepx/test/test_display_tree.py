#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""AUTHOR Romain Giot <romain.giot@ensicaen.fr>
In these tests, we want to verify if we can create an image of the tree.
"""

import unittest
import pystepx.graph.tree as gtree
import os.path

class TestDisplayTree(unittest.TestCase):
    """Launch tests to verify the hability display trees."""

    def setUp(self):
        """
        Clear the files
        """

        for file in ["test.png", "test.jpg"]:
            if os.path.exists(file):
                os.remove(file)

    def test_display(self):
        """Test the display of one tree."""

        tree = [(0, 1, 'root'), [(1, 2, '-'), [(1, 1, '^2'), [(1, 2, '-'), (3, 0, 'x'), (3, 0, 'x')]], [(1, 1, 'neg'), [(1, 2, '*'), (3, 0, 'x'), (3, 0, 'x')]]]]
        gt = gtree.DrawTree(tree, 'test', 'jpg')
        G = gt.draw()
        self.assertTrue(os.path.exists('test.jpg'))
        
        tree = [(0, 2, 'root'), [(2, 1, 'adf1'), [(1, 2, '+'), [(1, 2, '*'), [(1, 2, '*'), (3, 0, 'x'), (3, 0, 'x')], [(1, 2, '+'), (3, 0, 'x'), (3, 0, 'x')]], [(1, 2, '+'), [(1, 2, '+'), (3, 0, 'y'), (3, 0, 'x')], [(1, 2, '+'), (3, 0, 'x'), (3, 0, 'y')]]]], [(2, 1, 'adf2'), [(1, 2, 'adf2_+'), [(1, 2, 'adf2_*'), [(1, 2, 'adf2_+'), (5, 0, 'adf1'), (3, 0, 'y')], [(1, 2, 'adf2_*'), (5, 0, 'adf1'), (3, 0, 'y')]], [(1, 2, 'adf2_*'), [(1, 2, 'adf2_+'), (5, 0, 'adf1'), (3, 0, 'y')], [(1, 2, 'adf2_+'), (3, 0, 'y'), (3, 0, 'y')]]]]]
        gt = gtree.DrawTree(tree, 'test', 'jpg')
        G = gt.draw()


        tree = [(0, 2, 'root'), [(6, 1, 'ADF0'), [(1, 2, 'ADF0_+'), (8, 0, 'ADF0_PARAM0'), (8, 0, 'ADF0_PARAM1')]], [(0, 2, '_root'), [(7, 2, '_ADF0'), (3, 0, 'x'), (3, 0, 'x')], [(1, 2, '*'), (3, 0, 'x'), (3, 0, 'y')]]]
        gt = gtree.DrawTree(tree, 'test', 'jpg')
        G = gt.draw()

        print G.to_string()


if __name__ == "__main__":
    unittest.main()
