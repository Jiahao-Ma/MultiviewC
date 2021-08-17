# Toolkits for MultiviewC dataset
The MultiviewC dataset mainly contributes to multiview cattle action recognition, 3D objection detection and tracking. We build a novel synthetic dataset MultiviewC through UE4 based on [real cattle video dataset](https://cloudstor.aarnet.edu.au/plus/s/fouvWr9sE6TBueO) which is offered by CISRO. The format of our data set has been adjusted on the basis of [MultiviewX](https://github.com/hou-yz/MultiviewX) for set-up, annotation and files structure.

![alt text](https://github.com/Robert-Mar/MultiviewC/blob/main/github_material/gt.png "Visualization of ground true dataset")

The MultiviewC dataset is generated on a 37.5 meter by 37.5 meter square field. It contains 7 cameras monitoring cattle activities. The images in MultiviewC are of high resolution, 1280x720 and synthetic animals in our dataset are highly realistic. 

![alt text](https://github.com/Robert-Mar/MultiviewC/blob/main/github_material/MultiviewC.png "Visualization of MultiviewC")

The simulation dataset not only provide 3D and 2D object detection annotation, but also simulated the common activities of cattle on the farm, including walking, running, eating, idle and sleeping. To fully exploit the complementary, the intrinsic and extrinsic parameters of each camera are also provided in MultiviewC dataset.

![alt text](https://github.com/Robert-Mar/MultiviewC/blob/main/github_material/labeled_MultiviewC.png "Visualization of Labeled MultiviewC")
