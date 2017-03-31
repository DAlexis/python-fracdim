#!/usr/bin/env python3

from fracdim import TimeSeries as ts

import unittest
import numpy as np


class Test_intrateByCellSize(unittest.TestCase):
    def setUp(self):
        self.pointsCount = 100
        self.dim = 2
        self.points = np.ndarray(shape=(self.pointsCount, self.dim))

    def test_1(self):
        
        pass

