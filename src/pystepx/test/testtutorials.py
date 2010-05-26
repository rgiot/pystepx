#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Launch the test of the tutorials.
If one tutorial fails, there is a problem.
"""

import sys
sys.path.append("./..")

import unittest
from tutorials import Tutorial, Tutorial2, Tutorial3, Tutorial4, Tutorial5

class TutorialTestCase(unittest.TestCase):
    """
    class: TutorialTestCase
    =======================

    Manage the test of the tutorials
    """


    def testTutorial1(self):
        """
        Function testTutorial1
        ======================

        Test if tutorial 1 works correctly
        """
        test = Tutorial.Tutorial1()
        test.run()

    def testTutorial2(self):
        """
        Function testTutorial2
        ======================

        Test if tutorial 2 works correctly
        """
        test = Tutorial2.Tutorial2()
        test.run()

    def testTutorial3(self):
        """
        Function testTutorial3
        ======================

        Test if tutorial 3 works correctly
        """
        test = Tutorial3.Tutorial3()
        test.run()

    def testTutorial4(self):
        """
        Function testTutorial4
        ======================

        Test if tutorial 4 works correctly
        """
        test = Tutorial4.Tutorial4()
        test.run()

    def testTutorial5(self):
        """
        Function testTutorial5
        ======================

        Test if tutorial 5 works correctly
        """
        test = Tutorial5.Tutorial5()
        test.run()

def suite():
    """
    Function suite
    ==============
    Set up the test suit.
    """

    return unittest.makeSuite(TutorialTestCase,'test')



def main():
    """Launch the test procedure"""
    runner = unittest.TextTestRunner()
    runner.run(suite())

if __name__ == '__main__':
    #main()
    unittest.main()


