import unittest
import numpy as np

from fracdim import FracdimUtils as fu

class Test_rowToPoints(unittest.TestCase):
    def test_standard_case(self):
        testRow = [1,2,3,4,5,6,7,8,9,10]
        a = fu.rowToPoints(testRow, 3)
        self.assertEqual(  a[0,0], testRow[0])
        self.assertEqual(  a[1,0], testRow[1])
        self.assertEqual(  a[0,1], testRow[1])
        self.assertEqual(a[-1,-1], testRow[-1])

    def test_small_dataset1(self):
        testRow = [1, 2, 3, 4, 5, 6]
        a = fu.rowToPoints(testRow, 5)
        self.assertEqual(  a[0,0], testRow[0])
        self.assertEqual(  a[0,1], testRow[1])
        self.assertEqual(a[-1,-1], testRow[-1])

    def test_small_dataset2(self):
        testRow = [1, 2, 3, 4, 5]
        a = fu.rowToPoints(testRow, 5)
        self.assertEqual(  a[0,0], testRow[0])
        self.assertEqual(  a[0,1], testRow[1])
        self.assertEqual(a[-1,-1], testRow[-1])


class Test_MultiCell(unittest.TestCase):
    def test_creation(self):
        p1 = np.asarray([1, 1])
        p2 = np.asarray([3, 3])
        a = fu.MultiCell(2, p1, p2)

        p1 = np.ndarray(shape=(2))
        p2 = np.ndarray(shape=(3))
        self.assertRaises(Exception, fu.MultiCell, 3, p1, p2)

    def test_point_checking(self):
        p1 = np.asarray([1, 3, 1])
        p2 = np.asarray([3, 1, 3])

        ptest1 = np.asarray([2, 2, 2])
        ptest2 = np.asarray([2, 3.001, 2])
        ptest3 = np.asarray([0.999, 2, 2])

        a = fu.MultiCell(3, p1, p2)
        self.assertEqual( a.checkPoint(ptest1), True)
        self.assertEqual( a.checkPoint(ptest2), False)
        self.assertEqual( a.checkPoint(ptest3), False)

    def test_uninitialized_values(self):
        p1 = np.asarray([2, 1, 4])
        p2 = np.asarray([0, 3, -1])
        a = fu.MultiCell(3, p1, p2)

        self.assertEqual( a.userFlag, False)

    def test_setters_getters(self):
        p1 = np.asarray([2, 1, 4])
        p2 = np.asarray([0, 3, -1])
        a = fu.MultiCell(3, p1, p2)

        self.assertEqual(a.getMin()[0], 0)
        self.assertEqual(a.getMax()[0], 2)

        self.assertEqual(a.getMin()[1], 1)
        self.assertEqual(a.getMax()[1], 3)

        self.assertEqual(a.getMin()[2], -1)
        self.assertEqual(a.getMax()[2], 4)

class Test_BlocksCounter(unittest.TestCase):
    p1 = np.asarray([0, 0, 0])
    p2 = np.asarray([1, 1, 1])
    globalCell = fu.MultiCell(3, p1, p2)

    def test_creation(self):
        a = fu.BlocksCounter()
        a.setSize(self.globalCell)
        a.setCellsPerAxis(10)

    def test_counter_one_point(self):
        a = fu.BlocksCounter(cellsPerAxis=10, globalCell=self.globalCell)
        points = np.ndarray(3).reshape((1, 3))
        points[0, :] = [0.5, 0.5, 0.5]
        res = a.calculate(points)
        self.assertEqual(res, 1)

    def test_counter_two_points_in_one_cell(self):
        a = fu.BlocksCounter(cellsPerAxis=10, globalCell=self.globalCell)
        points = np.ndarray(6).reshape((2, 3))
        points[0, :] = [0.5, 0.5, 0.5]
        points[1, :] = [0.5, 0.5, 0.5]
        res = a.calculate(points)
        self.assertEqual(res, 1)

    def test_counter_two_points_in_different_cells(self):
        a = fu.BlocksCounter(cellsPerAxis=10, globalCell=self.globalCell)
        points = np.ndarray(6).reshape((2, 3))
        points[0, :] = [0.5, 0.5, 0.5]
        points[1, :] = [0.1, 0.5, 0.5]
        res = a.calculate(points)
        self.assertEqual(res, 2)

    def test_previous_counting_artifacts(self):
        a = fu.BlocksCounter(cellsPerAxis=10, globalCell=self.globalCell)
        points = np.ndarray(6).reshape((2, 3))
        points[0, :] = [0.5, 0.5, 0.5]
        points[1, :] = [0.1, 0.5, 0.5]
        res = a.calculate(points)
        self.assertEqual(res, 2)

        points[0, :] = [0.1, 0.3, 0.4]
        points[1, :] = [0.1, 0.3, 0.4]
        res = a.calculate(points)
        self.assertEqual(res, 1)

    def test_1d(self):
        p1 = np.asarray([0])
        p2 = np.asarray([1])
        globalCell = fu.MultiCell(1, p1, p2)
        a = fu.BlocksCounter(cellsPerAxis=20, globalCell=globalCell)

        points = np.ndarray(4).reshape((4, 1))
        points[0, :] = [0.1]
        points[1, :] = [0.7]
        points[2, :] = [0.62111]
        points[3, :] = [0.62112]
        self.assertEqual(a.calculate(points), 3)


if __name__ == "__main__":
    unittest.main()