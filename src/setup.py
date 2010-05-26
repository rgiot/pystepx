#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@author: by Romain Giot
@version: 1.30
@copyright: (c) 2010 Romain Giot under the mit license
http://www.opensource.org/licenses/mit-license.html
@contact: giot.romain at gmail.com
"""

"""
Installation file of the pystep library
"""

from distutils.core import setup
from distutils.extension import Extension

try:
  from Cython.Distutils import build_ext
except Exception:
  print 'You must install Cython'

try:
  import numpy as np
except Exception:
  print 'You must install numpy'

ext_modules = [
   Extension("pystepx.basewritepop",["pystepx/basewritepop.pyx"]),
   Extension("pystepx.baseevolver",["pystepx/baseevolver.pyx"]),
   Extension("pystepx.tree.treeconstants",["pystepx/tree/treeconstants.pyx"]),
   Extension("pystepx.tree.buildtree",["pystepx/tree/buildtree.pyx"]),
   Extension("pystepx.tree.numpyfunctions",["pystepx/tree/numpyfunctions.pyx"]),
   Extension("pystepx.fitness.evalfitness",["pystepx/fitness/evalfitness.pyx"]),
   Extension("pystepx.fitness.fitnessutil",["pystepx/fitness/fitnessutil.pyx"]),
   Extension("pystepx.geneticoperators.abstractoperator",["pystepx/geneticoperators/abstractoperator.pyx"]),
   Extension("pystepx.geneticoperators.crossoveroperator",["pystepx/geneticoperators/crossoveroperator.pyx"]),
   Extension("pystepx.geneticoperators.crossutil",["pystepx/geneticoperators/crossutil.pyx"]),
   Extension("pystepx.geneticoperators.mutationoperator",["pystepx/geneticoperators/mutationoperator.pyx"]),
   Extension("pystepx.geneticoperators.selection",["pystepx/geneticoperators/selection.pyx"]),
   Extension("pystepx.tutorials.santafetrail",["pystepx/tutorials/santafetrail.pyx"]),
   Extension("pystepx.tutorials.lawnmower",["pystepx/tutorials/lawnmower.pyx"]),
   ]

setup(name='pystepx',
      version='1.0.3',
      description='Python Strongly Typed Distributed Genetic Programming Library',
      author='Romain Giot/Mehdi Khoury',
      author_email='romain.giot@ensicaen.fr',
      url='',
      packages=['pystepx', 'pystepx.fitness', 'pystepx.geneticoperators',
                'pystepx.island', 'pystepx.test', 'pystepx.tree',
                'pystepx.tutorials'],
      cmdclass = {'build_ext': build_ext},
      ext_modules = ext_modules,
      include_dirs = [np.get_include()],
      requires=['sqlite3', 'ipython', 'numpy'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'Licence :: OSI Approved :: MIT License',
          'Topic :: Scientific/engineering :: Artificial Intelligence',
          ]

      )
