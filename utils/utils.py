import torch
import colorsys
import numpy as np
import torch.nn.functional as F
from PIL import Image, ImageDraw, ImageFont
from scipy.stats import multivariate_normal

def vis_colors(classes):
    hsv_tuples = [(x / len(classes), 1, 1) for x in range(len(classes))]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list( map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors) )
    return hsv_tuples, colors

def vis_styles(facecolor='red', alpha=0.5, size=10, color='black'):
    box = {"facecolor": facecolor, "alpha": alpha}
    styles = {"size": size, "color": color, "bbox": box}
    return styles

def m2cm(worldcoord, len_of_each_grid = 100):
    coord_x, coord_y = worldcoord
    coord_x = coord_x * len_of_each_grid
    coord_y = coord_y * len_of_each_grid
    return np.array([coord_x, coord_y], dtype=int)


def cm2m(worldcoord, len_of_each_grid = 100):
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

class GaussianKernel(object):
    def __init__(self, 
                save_dir=None,
                grid_reduce = 4,
                heatmaps = None
                ):
        self.save_dir = save_dir
        if heatmaps is not None:
            self.heatmaps = heatmaps
        else:
            self.heatmaps = list()
        map_sigma, map_kernel_size = 8 / grid_reduce, 8
        x, y = np.meshgrid(np.arange(-map_kernel_size, map_kernel_size + 1),
                           np.arange(-map_kernel_size, map_kernel_size + 1))
        pos = np.stack([x, y], axis=2)
        map_kernel = multivariate_normal.pdf(pos, [0, 0], np.identity(2) * map_sigma)
        map_kernel = map_kernel / map_kernel.max()
        kernel_size = map_kernel.shape[0]
        self.map_kernel = torch.zeros([1, 1, kernel_size, kernel_size], requires_grad=False)
        self.map_kernel[0, 0] = torch.from_numpy(map_kernel)

    def gaussian_kernel_heatmap(self, heatmap, box_cx, box_cy):
        heatmap[int(box_cy), int(box_cx)] = 1
        return heatmap

    def generate(self):
        # in order to boost the gaussian kernel heatmap generation,
        # send the tensor to default device: cuda:0
        device = torch.device('cpu')

        if isinstance(self.heatmaps, list):
            self.heatmaps = np.stack(self.heatmaps, axis=0)
        if isinstance(self.heatmaps, np.ndarray) and len(self.heatmaps.shape) !=3:
            self.heatmaps = self.heatmaps[np.newaxis, :, :]
        heatmaps = torch.Tensor(self.heatmaps)[:, None, :, :].to(device) # bs, 1, h, w
        mask = torch.where(heatmaps == 1.)
        with torch.no_grad(): 
            heatmaps = F.conv2d(heatmaps, self.map_kernel.float().to(device), \
                                padding=int((self.map_kernel.shape[-1] - 1) / 2))
            heatmaps[mask] = 1.
        self.heatmaps = heatmaps.squeeze(1).cpu().numpy()

    def viz_gk(self, rotate=False, save_dir=None):
        import matplotlib.pyplot as plt
        # heatmap = self.heatmaps[np.random.randint(len(self.heatmaps))]
        heatmap = self.heatmaps
        if len(heatmap.shape) != 2:
            heatmap = heatmap[0] # bs = 1 by default
        if rotate:
            heatmap = heatmap[:, ::-1]
            heatmap = heatmap[::-1, :]
        heatmap = (heatmap * 255).clip(0, 255).astype(np.uint8)
        plt.imshow(heatmap)
        plt.axis('off')
        if save_dir is not None:
            plt.savefig(save_dir, bbox_inches = 'tight',pad_inches = 0, dpi=300)
            plt.close()
        else:
            plt.show()