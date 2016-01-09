"""
Centrographic measures for point patterns

TODO

- ellipses
- euclidean median
- testing
- documentation

"""

__author__ = "Serge Rey sjsrey@gmail.com"

import sys
import numpy as np
import warnings
from scipy.spatial import ConvexHull


MAXD = sys.float_info.max
MIND = sys.float_info.min


def mbr(points):
    """
    Find minimum bounding rectangle of a point array.

    Arguments
    ---------
    points : arraylike
             (n,2), (x,y) coordinates of a series of event points.

    Returns
    -------
    min_x  : float
             leftmost value of the vertices of minimum bounding rectangle.
    min_y  : float
             downmost value of the vertices of minimum bounding rectangle.
    max_x  : float
             rightmost value of the vertices of minimum bounding rectangle.
    max_y  : float
             upmost value of the vertices of minimum bounding rectangle.

    """
    points = np.asarray(points)
    min_x = min_y = MAXD
    max_x = max_y = MIND
    for point in points:
        x, y = point
        if x > max_x:
            max_x = x
        if x < min_x:
            min_x = x
        if y > max_y:
            max_y = y
        if y < min_y:
            min_y = y
    return min_x, min_y, max_x, max_y


def hull(points):
    """
    Find convex hull of a point array.

    Arguments
    ---------
    points: arraylike
            (n,2), (x,y) coordinates of a series of event points.

    Returns
    -------
    _     : array
            (h,2), points defining the hull in counterclockwise order.
    """

    points = np.asarray(points)
    h = ConvexHull(points)
    return points[h.vertices]


def mean_center(points):
    """
    Find mean center of a point array.

    Arguments
    ---------
    points: arraylike
            (n,2), (x,y) coordinates of a series of event points.

    Returns
    -------
    _     : array
            (2,), (x,y) coordinates of the mean center.
    """

    points = np.asarray(points)
    return points.mean(axis=0)


def weighted_mean_center(points, weights):
    """
    Find weighted mean center of a marked point pattern.

    Arguments
    ---------
    points  : arraylike
              (n,2), (x,y) coordinates of a series of event points.
    weights : arraylike
              a series of attribute values of length n.
    Returns
    -------
    _      : array
             (2,), (x,y) coordinates of the weighted mean center.
    """


    points, weights = np.asarray(points), np.asarray(weights)
    w = weights * 1. / weights.sum()
    w.shape = (1, len(points))
    return np.dot(w, points)[0]


def manhattan_median(points):
    """
    Find manhattan median of a point array.

    Arguments
    ---------
    points  : arraylike
              (n,2), (x,y) coordinates of a series of event points.

    Returns
    -------
    _      : array
             (2,), (x,y) coordinates of the manhattan median.
    """

    points = np.asarray(points)
    if not len(points) % 2:
        s = "Manhattan Median is not unique for even point patterns."
        warnings.warn(s)
    return np.median(points, axis=0)


def std_distance(points):
    """
    Calculate standard distance of a point array.

    Arguments
    ---------
    points  : arraylike
              (n,2), (x,y) coordinates of a series of event points.

    Returns
    -------
    _      : float
             standard distance.
    """

    points = np.asarray(points)
    n, p = points.shape
    m = points.mean(axis=0)
    return np.sqrt(((points*points).sum(axis=0)/n - m*m).sum())


def ellipse(points):
    """
    Calculate parameters of standard deviational ellipse for a point pattern.

    Arguments
    ---------
    points : arraylike
             (n,2), (x,y) coordinates of a series of event points.

    Returns
    -------
    _      : float
             semi-major axis.
    _      : float
             semi-minor axis.
    theta  : float
             clockwise rotation angle of the ellipse.

    Implements approach from:

    https://www.icpsr.umich.edu/CrimeStat/files/CrimeStatChapter.4.pdf
    """

    points = np.asarray(points)
    n, k = points.shape
    x = points[:, 0]
    y = points[:, 1]
    xd = x - x.mean()
    yd = y - y.mean()
    xss = (xd * xd).sum()
    yss = (yd * yd).sum()
    cv = (xd * yd).sum()
    num = (xss - yss) + np.sqrt((xss - yss)**2 + 4 * (cv)**2)
    den = 2 * cv
    theta = np.arctan(num / den)
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    n_2 = n - 2
    sd_x = (2 * (xd * cos_theta - yd * sin_theta)**2).sum() / n_2
    sd_y = (2 * (xd * sin_theta - yd * cos_theta)**2).sum() / n_2
    return np.sqrt(sd_x), np.sqrt(sd_y), theta


def dtot(coord, points):
    """
    Sum of Euclidean distances between event points and a selected point.

    Arguments
    ---------
    coord   : arraylike
              (x,y) coordinates of a point.
    points  : arraylike
              (n,2), (x,y) coordinates of a series of event points.

    Returns
    -------
    d       : float
              sum of Euclidean distances.

    """
    points = np.asarray(points)
    xd = points[:, 0] - coord[0]
    yd = points[:, 1] - coord[1]
    d = np.sqrt(xd*xd + yd*yd).sum()
    return d

from scipy.optimize import minimize


def euclidean_median(points):
    """
    Calculate the Euclidean median for a point pattern.

    Arguments
    ---------
    points: arraylike
            (n,2), (x,y) coordinates of a series of event points.

    Returns
    -------
    _     : array
            (2,), (x,y) coordinates of the Euclidean median.

    """
    points = np.asarray(points)
    start = mean_center(points)
    res = minimize(dtot, start, args=points)
    return res['x']
