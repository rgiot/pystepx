#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test the island gp

"""

# imports
import unittest
import subprocess
import time

from pystepx.island.pystepislands import PySTEPXIsland
import pystepx.tutorials.functions_tutorial_island 

import logging


logging.basicConfig(level=logging.INFO)

# code
init_script = """from pystepx.tutorials.functions_tutorial_island import *;"""

class TestPystepIsland(unittest.TestCase):

    def __init__(self, a):
        """Start the processes."""
        super(TestPystepIsland, self).__init__(a)


    def setUp(self):
        """Initilize each thing."""
        return
        print 'Launch 4 clusters'
        subprocess.Popen("ipcluster start --n=4", shell=True, stdout=subprocess.PIPE)
        time.sleep(10)

    def tearDown(self):
        return
        print 'Close 4 clusters'
        subprocess.Popen("ipcluster stop", shell=True, stdout=subprocess.PIPE)

    def test_initialisation(self):
        """Test if we create correctly the objects"""
        self._pystepx = PySTEPXIsland(nb_islands=4, init_script=init_script)
        self._pystepx.__parametrize__()

        # Test if functions are equal
        f1 = pystepx.tutorials.functions_tutorial_island.treeRules
        for f2 in self._pystepx._rc[:]['treeRules']:
            self.assertEqual(f1, f2)


    def test_evolution(self):
        """Test if we are able to evolve"""
        self._pystepx = PySTEPXIsland(nb_islands=4, init_script=init_script)
        self._pystepx.evolve()

if __name__ == '__main__':
    unittest.main()


# metadata
__author__ = 'Romain Giot'
__copyright__ = 'Copyright 2011, ENSICAEN'
__credits__ = ['Romain Giot']
__licence__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Romain Giot'
__email__ = 'romain.giot@ensicaen.fr'
__status__ = 'Prototype'

