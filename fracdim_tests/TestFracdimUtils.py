#!/usr/bin/env python3

import unittest
import numpy as np

import fracdim
#from fracdim import FracdimUtils


class Test_rowToPoints(unittest.TestCase):
    def test_standard_case(self):
        testRow = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        a = fracdim.FracdimUtils.row_to_points(testRow, 3)
        self.assertEqual(  a[0,0], testRow[0])
        self.assertEqual(  a[1,0], testRow[1])
        self.assertEqual(  a[0,1], testRow[1])
        self.assertEqual(a[-1,-1], testRow[-1])

    def test_small_dataset1(self):
        testRow = [1, 2, 3, 4, 5, 6]
        a = fracdim.FracdimUtils.row_to_points(testRow, 5)
        self.assertEqual(  a[0,0], testRow[0])
        self.assertEqual(  a[0,1], testRow[1])
        self.assertEqual(a[-1,-1], testRow[-1])

    def test_small_dataset2(self):
        testRow = [1, 2, 3, 4, 5]
        a = fracdim.FracdimUtils.row_to_points(testRow, 5)
        self.assertEqual(  a[0,0], testRow[0])
        self.assertEqual(  a[0,1], testRow[1])
        self.assertEqual(a[-1,-1], testRow[-1])


class Test_getPointOnLine(unittest.TestCase):
    def test_1d_trivial(self):
        p1 = np.asarray([0])
        p2 = np.asarray([1])

        result = np.ndarray(shape=[1])
        value = 0.25
        fracdim.FracdimUtils.get_point_on_line(p1, p2, 0, value, result)
        self.assertEqual(result[0], value)

    def test_2d_target_between_points(self):
        p1 = np.asarray([1, 1])
        p2 = np.asarray([3, 2])
        result = np.ndarray(shape=[2])
        value = 2
        expectedResult = 1.5
        fracdim.FracdimUtils.get_point_on_line(p1, p2, 0, value, result)
        self.assertEqual(result[0], value)
        self.assertEqual(result[1], expectedResult)

    def test_2d_target_out_of_line(self):
        p1 = np.asarray([1, 1])
        p2 = np.asarray([3, 2])
        result = np.ndarray(shape=[2])
        value = 4
        expectedResult = 2.5
        fracdim.FracdimUtils.get_point_on_line(p1, p2, 0, value, result)
        self.assertEqual(result[0], value)
        self.assertEqual(result[1], expectedResult)

        value = 0
        expectedResult = 0.5
        fracdim.FracdimUtils.get_point_on_line(p1, p2, 0, value, result)
        self.assertEqual(result[0], value)
        self.assertEqual(result[1], expectedResult)


class Test_MultiCell(unittest.TestCase):
    def test_creation(self):
        p1 = np.asarray([1, 1])
        p2 = np.asarray([3, 3])
        a = fracdim.FracdimUtils.MultiCell(2, p1, p2)

        p1 = np.ndarray(shape=[2])
        p2 = np.ndarray(shape=[3])
        self.assertRaises(Exception, fracdim.FracdimUtils.MultiCell, 3, p1, p2)

    def test_point_checking(self):
        p1 = np.asarray([1, 3, 1])
        p2 = np.asarray([3, 1, 3])

        ptest1 = np.asarray([2, 2, 2])
        ptest2 = np.asarray([2, 3.001, 2])
        ptest3 = np.asarray([0.999, 2, 2])

        a = fracdim.FracdimUtils.MultiCell(3, p1, p2)
        self.assertEqual(a.check_point(ptest1), True)
        self.assertEqual(a.check_point(ptest2), False)
        self.assertEqual(a.check_point(ptest3), False)

    def test_uninitialized_values(self):
        p1 = np.asarray([2, 1, 4])
        p2 = np.asarray([0, 3, -1])
        a = fracdim.FracdimUtils.MultiCell(3, p1, p2)

        self.assertEqual( a.userFlag, False)

    def test_setters_getters(self):
        p1 = np.asarray([2, 1, 4])
        p2 = np.asarray([0, 3, -1])
        a = fracdim.FracdimUtils.MultiCell(3, p1, p2)

        self.assertEqual(a.get_min()[0], 0)
        self.assertEqual(a.get_max()[0], 2)

        self.assertEqual(a.get_min()[1], 1)
        self.assertEqual(a.get_max()[1], 3)

        self.assertEqual(a.get_min()[2], -1)
        self.assertEqual(a.get_max()[2], 4)


class Test_BlocksCounter(unittest.TestCase):
    p1 = np.asarray([0, 0, 0])
    p2 = np.asarray([1, 1, 1])
    globalCell = fracdim.FracdimUtils.MultiCell(3, p1, p2)

    def test_creation_mode_is_point(self):
        a = fracdim.FracdimUtils.BlocksCounter()
        a.set_size(self.globalCell)
        a.set_cells_per_axis(10)

    def test_counter_one_point_mode_is_point(self):
        a = fracdim.FracdimUtils.BlocksCounter(cellsPerAxis=10, globalCell=self.globalCell)
        points = np.ndarray(3).reshape((1, 3))
        points[0, :] = [0.5, 0.5, 0.5]
        res = a.calculate(points)
        self.assertEqual(res, 1)

    def test_counter_two_points_in_one_cell_mode_is_point(self):
        a = fracdim.FracdimUtils.BlocksCounter(cellsPerAxis=10, globalCell=self.globalCell)
        points = np.ndarray(6).reshape((2, 3))
        points[0, :] = [0.5, 0.5, 0.5]
        points[1, :] = [0.5, 0.5, 0.5]
        res = a.calculate(points)
        self.assertEqual(res, 1)

    def test_counter_two_points_in_different_cells_mode_is_point(self):
        a = fracdim.FracdimUtils.BlocksCounter(cellsPerAxis=10, globalCell=self.globalCell)
        points = np.ndarray(6).reshape((2, 3))
        points[0, :] = [0.5, 0.5, 0.5]
        points[1, :] = [0.1, 0.5, 0.5]
        res = a.calculate(points)
        self.assertEqual(res, 2)

    def test_previous_counting_artifacts_mode_is_point(self):
        a = fracdim.FracdimUtils.BlocksCounter(cellsPerAxis=10, globalCell=self.globalCell)
        points = np.ndarray(6).reshape((2, 3))
        points[0, :] = [0.5, 0.5, 0.5]
        points[1, :] = [0.1, 0.5, 0.5]
        res = a.calculate(points)
        self.assertEqual(res, 2)

        points[0, :] = [0.1, 0.3, 0.4]
        points[1, :] = [0.1, 0.3, 0.4]
        res = a.calculate(points)
        self.assertEqual(res, 1)

    def test_1d_mode_is_point(self):
        p1 = np.asarray([0])
        p2 = np.asarray([1])
        globalCell = fracdim.FracdimUtils.MultiCell(1, p1, p2)
        a = fracdim.FracdimUtils.BlocksCounter(cellsPerAxis=20, globalCell=globalCell)

        points = np.ndarray(4).reshape((4, 1))
        points[0, :] = [0.1]
        points[1, :] = [0.7]
        points[2, :] = [0.62111]
        points[3, :] = [0.62112]
        self.assertEqual(a.calculate(points), 3)

    def test_1d_test_boundaries_mode_is_point(self):
        p1 = np.asarray([0])
        p2 = np.asarray([1])
        globalCell = fracdim.FracdimUtils.MultiCell(1, p1, p2)
        count = 10
        a = fracdim.FracdimUtils.BlocksCounter(cellsPerAxis=count, globalCell=globalCell)

        points = np.ndarray(2).reshape((2, 1))
        points[0, :] = [0.0]
        points[1, :] = [1.0]
        self.assertEqual(a.calculate(points), 2)

    def test_1d_all_cells_with_points_mode_is_point(self):
        p1 = np.asarray([0])
        p2 = np.asarray([1])
        globalCell = fracdim.FracdimUtils.MultiCell(1, p1, p2)
        count = 10
        a = fracdim.FracdimUtils.BlocksCounter(cellsPerAxis=count, globalCell=globalCell)

        points = np.ndarray(count*2).reshape((count*2, 1))
        for i in range(0, count*2):
            points[i, :] = [i/(count*2)]

        self.assertEqual(a.calculate(points), count)

    # Now lets fracdim_tests mode="lines"

    def test_1d_test_boundaries_mode_is_lines(self):
        p1 = np.asarray([0])
        p2 = np.asarray([1])
        globalCell = fracdim.FracdimUtils.MultiCell(1, p1, p2)
        count = 10
        a = fracdim.FracdimUtils.BlocksCounter(cellsPerAxis=count, globalCell=globalCell, mode="lines")

        points = np.ndarray(2).reshape((2, 1))
        points[0, :] = [0.0]
        points[1, :] = [1.0]
        self.assertEqual(a.calculate(points), count)

    def test_2d_simple_line_mode_line(self):
        p1 = np.asarray([0, 0])
        p2 = np.asarray([10, 10])
        globalCell = fracdim.FracdimUtils.MultiCell(2, p1, p2)
        count = 10
        a = fracdim.FracdimUtils.BlocksCounter(cellsPerAxis=count, globalCell=globalCell, mode="lines")

        points = np.ndarray(4).reshape((2, 2))
        points[0, :] = [0.1, 0.1]
        points[1, :] = [9.9, 1.9]
        self.assertEqual(a.calculate(points), count+1)

        points[0, :] = [0.1, 0.1]
        points[1, :] = [9.9, 1.0] # Test for [1, 2) cell format
        self.assertEqual(a.calculate(points), count+1)

        points[0, :] = [0.1, 0.1]
        points[1, :] = [9.9, 0.9]
        self.assertEqual(a.calculate(points), count)

    def test_2d_poly_line_mode_line(self):
        p1 = np.asarray([0, 0])
        p2 = np.asarray([10, 10])
        globalCell = fracdim.FracdimUtils.MultiCell(2, p1, p2)
        count = 10
        a = fracdim.FracdimUtils.BlocksCounter(cellsPerAxis=count, globalCell=globalCell, mode="lines")

        points = np.ndarray(8).reshape((4, 2))
        # Trivial case
        points[0, :] = [0.5, 0.5]
        points[1, :] = [0.5, 0.5]
        points[2, :] = [0.5, 0.5]
        points[3, :] = [0.5, 0.5]
        self.assertEqual(a.calculate(points), 1)

        points[0, :] = [0.5, 0.5]
        points[1, :] = [9.5, 0.5]
        points[2, :] = [9.5, 1.5]
        points[3, :] = [0.5, 1.5]
        self.assertEqual(a.calculate(points), 2*count)

        points[0, :] = [0.5, 0.5]
        points[1, :] = [9.5, 1.5]
        points[2, :] = [0.5, 1.5]
        points[3, :] = [9.5, 2.5]
        self.assertEqual(a.calculate(points), 2*count+1)


if __name__ == "__main__":
    unittest.main()