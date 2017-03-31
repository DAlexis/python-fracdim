#!/usr/bin/env python3

import unittest
import numpy as np

from fracdim import FractalGenerator as fg


class Test_KochSnowflake(unittest.TestCase):
    def test_creation(self):
        a = fg.KochSnowflake()
        p = a.construct(3)
        a = fg.KochSnowflake()
        pp = a.construct(3)
