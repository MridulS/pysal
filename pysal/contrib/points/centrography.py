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
from math import pi as PI
from scipy.spatial import ConvexHull
from pysal.cg import get_angle_between
from pysal.cg.shapes import Ray
from scipy.spatial import distance as dist
from scipy.optimize import minimize

MAXD = sys.float_info.max
MIND = sys.float_info.min


def mbr(points):
    """
    Minimum bounding rectangle
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
    Find convex hull of a point array

    Arguments
    ---------

    points: array (n x 2)

    Returns
    -------
    _ : array (h x 2)
        points defining the hull in counterclockwise order
    """
    points = np.asarray(points)
    h = ConvexHull(points)
    return points[h.vertices]


def mean_center(points):
    points = np.asarray(points)
    return points.mean(axis=0)


def weighted_mean_center(points, weights):
    points, weights = np.asarray(points), np.asarray(weights)
    w = weights * 1. / weights.sum()
    w.shape = (1, len(points))
    return np.dot(w, points)[0]


def manhattan_median(points):
    points = np.asarray(points)
    if not len(points) % 2:
        s = "Manhattan Median is not unique for even point patterns."
        warnings.warn(s)
    return np.median(points, axis=0)


def std_distance(points):
    points = np.asarray(points)
    n, p = points.shape
    m = points.mean(axis=0)
    return np.sqrt(((points*points).sum(axis=0)/n - m*m).sum())


def ellipse(points):
    """
    Ellipse for a point pattern

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
    Sum of Euclidean distances between points and coord
    """
    points = np.asarray(points)
    xd = points[:, 0] - coord[0]
    yd = points[:, 1] - coord[1]
    d = np.sqrt(xd*xd + yd*yd).sum()
    return d

def euclidean_median(points):
    """
    Calculate the Euclidean median for a point pattern
    """
    points = np.asarray(points)
    start = mean_center(points)
    res = minimize(dtot, start, args=points)
    return res['x']

def skyum(points, is_hull=False):
    """
    Implements Skyum (1990)'s algorithm for the minimum bounding circle in R^2. 

    0. Store points in a linked list where point p can find prec(p) and succ(p),
    indicating the preceeding and succeeding points from p, moving clockwise, on
    the convex hull of points. 
    1. Find p in S that maximizes radius(prec(p), p, succ(p)) &
    angle(prec(p),p,succ(p)) in lexicographical order
    2a. If angle(prec(p), p, succ(p)) <= 90 degrees, then finish. 
    2b. If not, remove p from set. 
    """
    if not is_hull:
        points = hull(points)
    while len(points) > 1:
        angles = [_angle(_prec(p, points), p, _succ(p, points)) for p in points]
        circles = [_circle(_prec(p, points), p, _succ(p, points)) for p in points]
        radii = [c[0] for c in circles]
        lexmax = np.lexsort((radii, angles))[0]
        if angles[lexmax] > PI/2.0:
            points = points[points != points[,lexmax]]
        else:
            break
    return circles[lexmax]

def _angle(p,q,r):
    return get_angle_between(Ray(q,p),Ray(q,r))

def _prec(p,l):
    return l[l.index(p)-1]

def _succ(p,l):
    return l[l.index(p)+1]

def _circle(p,q,r, dmetric=dist.euclidean):
    """
    Returns (radius, (center_x, center_y)) of the circumscribed circle by the
    triangle pqr.
    """
    px,py = p
    qx,qy = q
    rx,ry = r
    D = 2*(px*(qy - ry) + qx*(ry - py) + rx*(py - qy))
    center_x = ((px**2 + py**2)*(qy-ry) + (qx**2 + qy**2)(ry-py) 
              + (rx**2 + ry**2)*(py-qy)) / D
    center_y = ((px**2 + py**2)*(ry-qy) + (qx**2 + qy**2)(py-ry) 
              + (rx**2 + ry**2)*(qy-py)) / D
    radius = dmetric((center_x, center_y), p)
    return radius, (center_x, center_y)
