import json, os, cv2
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from utils.utils import draw_3DBBox, vis_colors, vis_styles, compute_3d_bbox, corners8_to_rect4, GaussianKernel
from adjustText import adjust_text

intrinsic_camera_matrix_filenames = ['intr_Camera1.xml', 'intr_Camera2.xml', 'intr_Camera3.xml', 'intr_Camera4.xml',
                                     'intr_Camera5.xml', 'intr_Camera6.xml', 'intr_Camera7.xml']
extrinsic_camera_matrix_filenames = ['extr_Camera1.xml', 'extr_Camera2.xml', 'extr_Camera3.xml', 'extr_Camera4.xml',
                                     'extr_Camera5.xml', 'extr_Camera6.xml', 'extr_Camera7.xml']

class MultiviewCow(object):
    def __init__(self, root = r'.',
                       ann_root=r'annotations', 
                       img_root =r'images', 
                       calib_root=r'calibrations', 
                       cam_range=range(1, 8),
                       ) -> None:
        super().__init__()
        """
            json_root: annotation path
            img_root: image path
            calib_root: calibration path
            cam_range: default value: range(1, 8), represent the camera ID

            # MultiviewC Map Setting: 
            #     Size of farm: w=3900(cm) h=3900(cm)
          

            # MultiviewC Camera Setting:
            #     theta_ref_global = theta_w_global + 90
            #     theta_c_global = theta_ref_global - R_z
            #     theta_c_global = theta_local + theta_ray
                                    
            #     theta_c_global = theta_w_global + 90 - R_z = theta_local + theta_ray
                
            #     R_z: the rotation angle of 7 cameras on Z-axis of the world coordinate in the farm 
            #             [133.861435, -135.736145, -45.890991, 48.889431, 90.000084, 121.566719, 59.132477] 
            #     theta_ray: the angle between the ray from cammera center to objects' center 
            #                 and the y axis of camera.  (angle of camera coordinate) (-pi/2, pi/2)
            #     NOTICE: we need to keep theta_c_global in range [-pi, pi]
        """
        self.ann_root = os.path.join(root, ann_root)
        self.img_root = os.path.join(root, img_root)
        self.calib_root = os.path.join(root, calib_root)
        self.cam_range = cam_range

    def __len__(self):
        return len(os.listdir(self.ann_root))

    def get_intrinsic_extrinsic_matrix(self, camera_i):
        intrinsic_camera_path = os.path.join(self.calib_root, 'intrinsic')
        fp_calibration = cv2.FileStorage(os.path.join(intrinsic_camera_path,
                                                        intrinsic_camera_matrix_filenames[camera_i]),
                                            flags=cv2.FILE_STORAGE_READ)
        intrinsic_matrix = fp_calibration.getNode('camera_matrix').mat()
        fp_calibration.release()

        extrinsic_camera_path = os.path.join(self.calib_root, 'extrinsic')
        fp_calibration = cv2.FileStorage(os.path.join(extrinsic_camera_path,
                                                        extrinsic_camera_matrix_filenames[camera_i]),
                                            flags=cv2.FILE_STORAGE_READ)
        rvec, tvec = fp_calibration.getNode('rvec').mat().squeeze(), fp_calibration.getNode('tvec').mat().squeeze()
        R_z = fp_calibration.getNode('R_z').real()
        fp_calibration.release()

        rotation_matrix, _ = cv2.Rodrigues(rvec)
        translation_matrix = np.array(tvec, dtype=np.float).reshape(3, 1)
        extrinsic_matrix = np.hstack((rotation_matrix, translation_matrix))

        return intrinsic_matrix, extrinsic_matrix, R_z
    
    def __getitem__(self, index):
        """ 
        Returns:
            annotations: `dict`, contains the label information of all perpespectives (7 views) at this moment
                [FORMAT]
                    "C1":[
                        {
                            "CowID": "Cow0",
                            "action": "sleep",
                            "location": [
                                1900,
                                1874,
                                0
                            ],
                            "rotation": -172,
                            "dimension": [
                                114,
                                150,
                                278 ] 
                        },
                        ...
                    ],
                    "C2":[
                        ...
                    ],
                    ...
                    "C7":[
                        ...
                    ]
            image_fnames: `list`, stores images path of all perpespectives (7 views) at this moment
            calib_fnames: `list`, stores calibration files path of 7 views

        """
        ann_fname = self.ann_root + '\\{:04d}.json'.format(index)
        image_fnames = [ os.path.join(self.img_root, 'C{}\\{:04d}.png'.format(cam_id, index))for cam_id in self.cam_range ]
       
        with open(ann_fname, 'r') as f:
            annotations = json.load(f)
        return annotations, image_fnames
    
    def visualize(self, index, camid, fontsize=8, show_2D_bbox=False, figsize=(15, 8), linewidth3D=2, linewidth2D=1.5):
        """
            Args:
                annotations: `dict`, contains the label information of all perpespectives (7 views) at this moment.
                            Data format has been mentioned in the comment of `__getitem__()` function .
                image_fnames: `list`, stores images path of all perpespectives (7 views) at this moment
                calib_fnames: `list`, stores calibration file path of 7 views
        """
        assert camid in range(0, 7), "camera index ranges from 0 to 6"

        # save
        save_root = r'F:\ANU\ENGN8602\Data\MultiviewC_github\MultiviewC\viz_images'
        if not os.path.exists(save_root):
            os.mkdir(save_root)
        save_cam_root = os.path.join(save_root, "C{}".format(camid+1))
        if not os.path.exists(save_cam_root):
            os.mkdir(save_cam_root)
        img_save_path = os.path.join(save_cam_root, '{:03d}.png'.format(index))
        if os.path.exists(img_save_path):
            print(img_save_path, 'exists. Continue')
            return 
        
        annotations, image_fnames = self.__getitem__(index)
        annotation = annotations['C{}'.format(camid+1)]
        image_fname = image_fnames[camid]
        #--------------------------------#
        # read calibration and image
        #--------------------------------#
        intrinsic_matrix, extrinsic_matrix, _ = self.get_intrinsic_extrinsic_matrix(camid)
        project_mat = intrinsic_matrix @ extrinsic_matrix

        image = Image.open(image_fname)
        H, W, _ = np.array(image).shape
        #------------#
        # front color
        #------------#
        classes = ['Cow{}'.format(x) for x in range(0, 15)]
        hsv_tuples, _ = vis_colors(classes)
        styples = vis_styles()
        #------------#
        # visualization
        #------------#
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        ax.imshow(image)
        ax.axis('off')
        plt.xlim(0, 1280)
        plt.ylim(720, 0)
        new_texts = list()
        for ann in annotation:
            # read annotation and compute 3D bbox in 2D image
            visible = ann['visible']
            if not visible:
                continue 
            label = ann['CowID']
            action = ann['action']
            location = ann['location']
            rotation = ann['rotation']
            dimension = ann['dimension']
            corner_2d = compute_3d_bbox(dimension, rotation, location, project_mat)
            # mask = np.logical_and(corner_2d[:, 0] > 0 , corner_2d[:, 0] < 1280) & np.logical_and(corner_2d[:, 1] > 0 , corner_2d[:, 1] < 720)[0]
            
            # corner_2d = corner_2d[mask]
            if len(corner_2d) != 8:
                continue
            [xmin, ymin, xmax, ymax] = corners8_to_rect4(corner_2d)

            # visualization setting
            c = hsv_tuples[classes.index(label)]
            styples['bbox']['facecolor'] = c
            styples['size'] = fontsize
            if show_2D_bbox:
                width = xmax - xmin 
                height = ymax - ymin
                rect = plt.Rectangle([xmin, ymin], width, height, color=(1, 0, 0), linewidth=linewidth2D, fill=False)
                ax.add_patch(rect)
            ax = draw_3DBBox(ax, corner_2d, edgecolor=(0, 1, 0),linewidth=linewidth3D)
            new_texts.append(ax.text(corner_2d[4][0], corner_2d[4][1]-15, s='{}: {}'.format(label, action), **styples, clip_on=True))
        # adjust text location
        adjust_text(new_texts, 
            only_move={'text': 'x'},
            save_steps=False)
        
        plt.savefig(img_save_path, bbox_inches = 'tight',pad_inches = 0, dpi=300)
        # plt.show()
        plt.close()
        return ax
    
    def save_bev_label(self, img_indx):
        save_dir = r'F:\ANU\ENGN8602\Data\MultiviewC_github\MultiviewC\viz_images\Z_BEV'
        save_dir = os.path.join(save_dir, "{:03}.png".format(img_indx))
        annotations, image_fnames = self.__getitem__(img_indx)
        annotation = annotations['C1']
        save_root = r'F:\ANU\ENGN8602\Data\MultiviewC_github\MultiviewC\viz_images\Z_BEV'
        if not os.path.exists(save_root):
            os.mkdir(save_root)
        heatmap = np.zeros(shape=(156, 156))
        gk = GaussianKernel(heatmaps=heatmap)
        for ann in annotation:
            location = np.array(ann['location'][:2])
            """
            # `25` is scale factor from world_coord to world grid. 
            # See https://github.com/Robert-Mar/VFA/blob/main/vfa/data/multiviewC.py
            # the value of `cube_LWH` in class MultiviewC params 
            """
            location = location / 25
            heatmap = gk.gaussian_kernel_heatmap(heatmap, location[0], location[1])
        gk.generate()
        gk.viz_gk(True, save_dir)
        pass


if __name__ == '__main__':
    import sys
    dataset = MultiviewCow()
    for img_id in range(len(dataset)):
        if img_id <=9:
            continue
        annotations, image_fnames = dataset[img_id]
        for cam_id in range(0,7):
            dataset.visualize(index=img_id, camid=cam_id, show_2D_bbox=True, linewidth3D=1.5, linewidth2D=2)
        dataset.save_bev_label(img_id)
        print('[{}/{}] Complete.'.format(img_id, len(dataset)))
