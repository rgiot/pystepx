#!/usr/bin/env python
# encoding: utf-8
# filename: twoboxes_profile.py
import logging
logging.basicConfig(level=logging.DEBUG)

if 0:
  PROF='Profile_gen0.prof'
else:
  PROF='Profile_gen1.prof'

import pstats, cProfile

import pystepx.tutorials.twoboxes

cProfile.runctx("pystepx.tutorials.twoboxes.main()", globals(), locals(), PROF)

s = pstats.Stats(PROF)
s.strip_dirs().sort_stats("time").print_stats()
