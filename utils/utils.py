import numpy as np
from PIL import Image, ImageDraw, ImageFont
import colorsys

def vis_colors(classes):
    hsv_tuples = [(x / len(classes), 1., 1.) for x in range(len(classes))]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list( map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors) )
    return hsv_tuples, colors

def vis_styles(facecolor='red', alpha=0.5, size=10, color='black'):
    box = {"facecolor": facecolor, "alpha": alpha}
    styles = {"size": size, "color": color, "bbox": box}
    return styles

def get_worldgrid_from_worldcoord(worldcoord, len_of_each_grid = 100):
    coord_x, coord_y = worldcoord
    coord_x = coord_x * len_of_each_grid
    coord_y = coord_y * len_of_each_grid
    return np.array([coord_x, coord_y], dtype=int)


def get_worldcoord_for_imagecoord(worldcoord, len_of_each_grid = 100):
    if isinstance(worldcoord, list):
        worldcoord = [c / len_of_each_grid for c in worldcoord]
        return worldcoord
    worldcoord = worldcoord / len_of_each_grid
    return worldcoord
    
def corners8_to_rect4(corners8):
    xmin = np.min(corners8[:, 0])
    ymin = np.min(corners8[:, 1])
    xmax = np.max(corners8[:, 0])
    ymax = np.max(corners8[:, 1])
    return [xmin, ymin, xmax, ymax]

def rotz(t):
    """ Rotation about z-axis """
    c = np.cos(t)
    s = np.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def project_to_image(corner_3d, calib):
    """ Project corner_3d `nx4 points` in camera rect coord to image2 plane
        Args:
            corner_3d: nx4 `numpy.ndarray`
            calib: camera projection matrix
        Returns:
            corner_2d: nx2 `numpy.ndarray` 2d points in image2
    """
    corner_2d = np.dot(calib, corner_3d.T)
    corner_2d[0, :] = corner_2d[0, :] / corner_2d[2, :]
    corner_2d[1, :] = corner_2d[1, :] / corner_2d[2, :]
    corner_2d = np.array(corner_2d, dtype=np.int)
    return corner_2d[0:2, :].T


def compute_3d_bbox(dimension, rotation, location, calib):
    dimension = get_worldcoord_for_imagecoord(dimension)
    location = get_worldcoord_for_imagecoord(location)
    h, w, l = dimension[0], dimension[1], dimension[2]
    x = [-l / 2, l / 2, l / 2, -l / 2, -l / 2, l / 2, l / 2, -l / 2]
    y = [-w / 2, -w / 2, w / 2, w / 2, -w / 2, -w / 2, w / 2, w / 2]
    z = [0, 0, 0, 0, h, h, h, h]

    rotMat = rotz(np.deg2rad(rotation))
    corner_3d = np.vstack([x, y, z])
    corner_3d = np.dot(rotMat, corner_3d)
    bottom_center = np.tile(location, (corner_3d.shape[1], 1)).T
    corner_3d = corner_3d + bottom_center
    corner_3d_homo = np.vstack([corner_3d, np.ones((1, corner_3d.shape[1]))])
    corner_2d = project_to_image(corner_3d_homo.T, calib)
    return corner_2d

def draw_3DBBox(ax, corners, edgecolor=(0, 1, 0), linewidth=1):
    if len(corners) != 8:
        return ax
    assert corners.shape[1] == 2, 'corners` shape should be [8, 2]'
    for k in range(0, 4):
        i, j = k, (k + 1) % 4
        ax.plot((corners[i, 0], corners[j, 0]), (corners[i, 1], corners[j, 1]), color=edgecolor, linewidth=linewidth)
        i, j = k + 4, (k + 1) % 4 + 4
        ax.plot((corners[i, 0], corners[j, 0]), (corners[i, 1], corners[j, 1]), color=edgecolor, linewidth=linewidth)
        i, j = k, k + 4
        ax.plot((corners[i, 0], corners[j, 0]), (corners[i, 1], corners[j, 1]), color=edgecolor, linewidth=linewidth)
    return ax