# MultiviewC dataset toolkits and engine! 
## MultiviewC engine based on UE4.
MultiviewC engine, the platform that support for multi-person online data collection, are released! 
![alt text](https://github.com/Robert-Mar/MultiviewC/tree/main/github_material/MulitiviewC_nolabel.gif "7 cameras view in MultiviewC dataset.") 

The engine captures accurate 3D and 2D information of the target (cattle), as well as the target's movements and the spatial distribution of the farm. 
![alt text](https://github.com/Robert-Mar/MultiviewC/tree/main/github_material/MulitiviewC_nolabel.gif "Labeled targets in 7 view and occupancy map.") 

## Toolkits for MultiviewC dataset

### Overview
The MultiviewC dataset mainly contributes to multiview cattle action recognition, 3D objection detection and tracking. We build a novel synthetic dataset MultiviewC through UE4 based on [real cattle video dataset](https://cloudstor.aarnet.edu.au/plus/s/fouvWr9sE6TBueO) which is offered by CISRO. The format of our data set has been adjusted on the basis of [MultiviewX](https://github.com/hou-yz/MultiviewX) for set-up, annotation and files structure.

![alt text](https://github.com/Robert-Mar/MultiviewC/blob/main/github_material/gt.png "Visualization of ground true dataset")

The MultiviewC dataset is generated on a 37.5 meter by 37.5 meter square field. It contains 7 cameras monitoring cattle activities. The images in MultiviewC are of high resolution, 1280x720 and synthetic animals in our dataset are highly realistic. 

![alt text](https://github.com/Robert-Mar/MultiviewC/blob/main/github_material/MultiviewC.png "Visualization of MultiviewC")

The simulation dataset not only provide 3D and 2D object detection annotation, but also simulated the common activities of cattle on the farm, including walking, running, eating, idle and sleeping. To fully exploit the complementary, the intrinsic and extrinsic parameters of each camera are also provided in MultiviewC dataset.

![alt text](https://github.com/Robert-Mar/MultiviewC/blob/main/github_material/labeled_MultiviewC.png "Visualization of Labeled MultiviewC")

### Project structure
| File                   | Description                                                                                      |
| ---------------------- | ------------------------------------------------------------------------------------------------ |
| `data.py`  | Methods for dataset visualisation and parsing labels, calibration information and images                                |
| `./utils/utils.py`  | Methods for projecting 3D bounding box to 2D image and how to generate 3D bbox in our simulation dataset coordinate  |

### Dataset
Download the data (images, annotation, calibrations) from [BaiduDrive](https://pan.baidu.com/s/1s67xf8eznms3eF6GfluYSg)(pwd:6666) or [GoogleDrive](https://drive.google.com/file/d/1OrSDryc7DRxKerhHN-g648sI1VgmlbrI/view?usp=sharing). We have updated a new annotation which has labeled the visibility of each cow at each frame. 

The dataset folder structure is as following:
```
MultiviewC
├── annotations
|   ├── 0000.json
|   ├── 0001.json
|       ...
|       
├── calibrations
|   ├── Camera1
|   |   └── parameters.json
|   ├── Camera2
|   |    ...
|   └── Camera7
|        
└── images
    ├── C1
    |   ├── 0000.png
    |   ├── 0001.png
    |       ...
    ├── C2
    |   ...
    └── C7 
```

### Toolkits for MultiviewC dataset.

The repo includes the toolkits and utilities for building MultiviewC dataset.

How to's
- download (from [Baidu Drive](https://pan.baidu.com/s/1s67xf8eznms3eF6GfluYSg) `Extraction Code: 6666` or [GoogleDrive](https://drive.google.com/file/d/1OrSDryc7DRxKerhHN-g648sI1VgmlbrI/view?usp=sharing) and copy the `annotations`, `images` and `calibrations` folder into this repo. 
- run the following command.
```shell script
python data.py
```
- done.
