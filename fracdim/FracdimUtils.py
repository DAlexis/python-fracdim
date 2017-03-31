import numpy as np
import math


def row_to_points(row, dimension):
    """
    Transform discrete row to an array of points this way:
    row_to_points([a, b, c, d, e, f, g, h, k], 3) gives
    [[a, b, c],
     [b, c, d],
     [d, e, f],
     [e, f, g],
     [f, g, h],
     [g, h, k]]
    :param row: discrete row
    :param dimension: dimension of points space
    :return: result of operation
    """
    rowLen = len(row)
    pointsCount = rowLen-dimension+1
    if pointsCount < 1:
        return 0

    a = np.ndarray(shape=(pointsCount, dimension))

    for i in range(0, pointsCount):
        for j in range(0, dimension):
            a[i, j] = row[i+j]
    return a


def get_point_on_line(lineBegin, lineEnd, axis, axisValue, targetPoint):
    """
    Get point on line by one given coordinate
    :param lineBegin: first fixed point on line
    :param lineEnd: second fixed point
    :param axis: known coordinate axis index
    :param axisValue: known coordinate
    :param targetPoint: function output
    :return:
    """
    dim = lineBegin.shape[0]
    targetPoint[axis] = axisValue
    progress = (axisValue - lineBegin[axis]) / (lineEnd[axis] - lineBegin[axis])
    for i in range(0, dim):
        if i == axis:
            continue
        targetPoint[i] = (1-progress) * lineBegin[i] + progress * lineEnd[i]


class MultiCell:
    """
        Rectangular cell in multi-dimensional space
    """
    def __init__(self, dim, p1=None, p2=None):
        self.userFlag = False
        self.__dim = 1
        self.__minCorner = None
        self.__maxCorner = None

        if p1 is not None and p1.shape != (dim,):
            raise Exception("Invalid pmin shape")

        if p1 is not None and p2.shape != (dim,):
            raise Exception("Invalid pmax shape")

        self.__dim = dim
        self.__minCorner = np.ndarray(shape=(dim))
        self.__maxCorner = np.ndarray(shape=(dim))

        if (p1 is not None) and (p2 is not None):
            for i in range(0, dim):
                if p1[i] > p2[i]:
                    self.__maxCorner[i] = p1[i]
                    self.__minCorner[i] = p2[i]
                else:
                    self.__maxCorner[i] = p2[i]
                    self.__minCorner[i] = p1[i]
        else:
            if p1 is not None:
                self.__minCorner = p1

            if p2 is not None:
                self.__maxCorner = p2

    def set(self, pmin=None, pmax=None):
        if pmin is not None:
            self.__minCorner = pmin

        if pmax is not None:
            self.__maxCorner = pmax

    def get_min(self):
        return self.__minCorner

    def get_max(self):
        return self.__maxCorner

    def check_point(self, p):
        lenP = len(p)
        if lenP > len(self.__minCorner):
            raise Exception("Invalid point dimension")

        for i in range(0, lenP):
            if p[i] < self.__minCorner[i] or p[i] > self.__maxCorner[i]:
                return False

        return True

    def dim(self):
        return self.__dim


class MultiGrid:
    """
        Multi-dimensional space grid of rectangular cells
        NOT IMPLEMENTED
    """
    def __init__(self):
        self.__globalCell = None
        self.__cells = None
        self.__cellsPerAxis = 0

    def get_cell(self, indices):
        index = 0
        for i in reversed(indices):
            index = index * self.__cellsPerAxis + i
        return self.__cells[index]

    def build(self, global_cell, cells_count_per_axis):
        self.__globalCell = global_cell
        self.__cellsPerAxis = cells_count_per_axis
        __cells = []

    def __recursive_add_cells(self, currentDim, offset):
        for i in range(0, self.__cellsPerAxis):
            pass  # TODO implement from here when this class is needed


class BlocksCounter(object):
    """
    This class calculates count of blocks that concrete dataset included to.
    """

    def __init__(self, globalCell=None, cellsPerAxis=1, mode="points"):
        """
        Constructor that configure BlocksCounter
        :param globalCell: MultiCell object describes area of blocks counting
        :param cellsPerAxis: Axis division method
        :param mode: "points" means than only points inclusions will be accounted,
                     "lines" means than lines connecting points will be accounted too. NOT IMPLEMENTED
        :return: constructed object
        """
        if mode != "points" and mode != "lines":
            raise Exception("Invalid mode for BlocksCounter")

        self.__globalCell = None
        self.__offsets = []
        self.__cellsPerAxis = 0
        self.__cell_has_point = None
        self.__mode = mode
        self.__dim = 0

        if globalCell is not None:
            self.set_size(globalCell)
            self.set_cells_per_axis(cellsPerAxis)

    def set_size(self, cell):
        self.__globalCell = cell
        self.__dim = cell.dim()

    def set_cells_per_axis(self, cells_per_axis):
        self.__cellsPerAxis = cells_per_axis
        self.__offsets.append(1)
        for i in range(0, self.__globalCell.dim()-1):
            self.__offsets.append(self.__offsets[i] * cells_per_axis)

        self.__cell_has_point = np.ndarray(self.__offsets[-1] * self.__cellsPerAxis)
        self.__cell_has_point[:] = 0

    def calculate(self, points):
        if self.__mode == "points":
            return self.__calculate_points(points)
        else:
            return self.__calculate_lines(points)

    def __mark_visited(self, indices):
        """
        Mark cell visited by its indices
        :param indices: cell ids
        :return: nothing
        """
        index = 0
        for i in reversed(indices):
            index = index * self.__cellsPerAxis + i
        self.__cell_has_point[index] = 1

    def __get_point_indexes(self, point, indices):
        for i in range(0, self.__globalCell.dim()):
            tmp = (point[i] - self.__globalCell.get_min()[i]) \
                  / (self.__globalCell.get_max()[i] - self.__globalCell.get_min()[i])
            index = int(tmp * self.__cellsPerAxis)
            # For right boundary values than formally does not imcluded to system
            # because cells are alike [0, 1), [1, 2), ... , [9, 10) <-- this border
            # should not be open
            if index == self.__cellsPerAxis:
                index = self.__cellsPerAxis-1

            indices[i] = index

    def __index_to_lower_boundary_coordinate(self, axis, index):
        return self.__globalCell.get_min()[axis] + \
               (self.__globalCell.get_max()[axis] - self.__globalCell.get_min()[axis]) * \
               (index / self.__cellsPerAxis)

    def __get_cell_size(self, axis):
        return (self.__globalCell.get_max()[axis] - self.__globalCell.get_min()[axis]) / self.__cellsPerAxis

    def __calculate_lines(self, points):
        self.__cell_has_point[:] = 0
        if points.shape[0] == 1:
            return 1

        begin_indexes = np.ndarray(self.__globalCell.dim(), dtype=int)
        end_indexes = np.ndarray(self.__globalCell.dim(), dtype=int)
        indexes = np.ndarray(self.__globalCell.dim(), dtype=int)

        middle_point = np.ndarray(self.__globalCell.dim())

        self.__get_point_indexes(points[0, :], begin_indexes)
        for pointIndex in range(1, points.shape[0]):
            self.__get_point_indexes(points[pointIndex, :], end_indexes)
            self.__mark_visited(end_indexes)
            self.__mark_visited(begin_indexes)
            # Iterating by all dimensions to find all crossings of line with grid
            for d in range(0, self.__dim):
                # Now iterating by cells crossing along this dimension
                begin = min(begin_indexes[d], end_indexes[d]) + 1
                end = max(begin_indexes[d], end_indexes[d])

                for i in range(begin, end+1):
                    # We have crossing with i's cell lowest border on axis d
                    get_point_on_line(lineBegin=points[pointIndex - 1, :],
                                      lineEnd=points[pointIndex, :],
                                      axis=d,
                                      axisValue=self.__index_to_lower_boundary_coordinate(axis=d, index=i),
                                      targetPoint=middle_point)
                    # a little move of border point inside cell
                    middle_point[d] -= self.__get_cell_size(d) * 0.1
                    self.__get_point_indexes(middle_point, indexes)
                    self.__mark_visited(indexes)

            begin_indexes = end_indexes.copy()

        result = 0
        for m in self.__cell_has_point:
            if m != 0:
                result += 1

        return result

    def __calculate_points(self, points):
        self.__cell_has_point[:] = 0

        indexes = np.ndarray(self.__globalCell.dim(), dtype=int)
        for i in range(0, points.shape[0]):
            self.__get_point_indexes(points[i, :], indexes)
            self.__mark_visited(indexes)

        result = 0

        for m in self.__cell_has_point:
            if m != 0:
                result += 1

        return result


def calculate_blocks_count_1d(data, block_size):
    pass
