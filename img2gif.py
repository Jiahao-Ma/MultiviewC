import os
from pathlib import Path
from PIL import Image

def imgs2gif(imgPaths, saveName, duration=None, loop=0, fps=None):
    """
    生成动态图片 格式为 gif
    :param imgPaths: 一系列图片路径
    :param saveName: 保存gif的名字
    :param duration: gif每帧间隔 单位 秒
    :param fps: 帧率
    :param loop: 播放次数（在不同的播放器上有所区别）， 0代表循环播放
    :return:
    """
    if fps:
        duration = 1 / fps
    duration *= 1000
    imgs = [Image.open(str(path)) for path in imgPaths]
    imgs[0].save(saveName, save_all=True, append_images=imgs, duration=duration, loop=loop)




def catImg2x4(img_root, W=640, H=360, save_root='cat_images'):
    files = os.listdir(os.path.join(img_root, 'Z_BEV'))
    folders = [os.path.join(img_root, p) for p in os.listdir(img_root)]
    for file in files:
        img_paths = list()
        for folder in folders:
            img_paths.append(os.path.join(folder, file))
        cated_img = Image.new('RGB', (W*4, H*2), color=0)
        for id, p in enumerate(img_paths):
            if id == len(img_paths)-1:
                img = Image.open(p).resize((H, H), Image.LANCZOS)
            else:
                img = Image.open(p).resize((W, H), Image.LANCZOS)
            row_id = id // 4
            col_id = id % 4
            if id == len(img_paths)-1:
                cated_img.paste(img, box=(col_id*W+(W - H)//2, row_id*H))
            else:
                cated_img.paste(img, box=(col_id*W, row_id*H))
        if not os.path.exists(save_root):
            os.mkdir(save_root)
        cated_img.save(os.path.join(save_root, '2x4', file))
        print(file, 'has been saved in ', save_root)

def catImg1x7(img_root, W=640, H=360, save_root='cat_images'):
    files = os.listdir(os.path.join(img_root, 'C1'))
    folders = [os.path.join(img_root, p) for p in os.listdir(img_root)]
    for file in files:
        img_paths = list()
        for folder in folders:
            img_paths.append(os.path.join(folder, file))
        cated_img = Image.new('RGB', (W*7, H), color=0)
        for id, p in enumerate(img_paths):
            img = Image.open(p).resize((W, H), Image.LANCZOS)
            cated_img.paste(img, box=(id*W, 0))
        if not os.path.exists(save_root):
            os.mkdir(save_root)
        cated_img.save(os.path.join(save_root, '1x7', file))
        print(file, 'has been saved in ', save_root)
        

# concatnate images
# catImg2x4(r'viz_images')
catImg1x7(r'images')

# gif generate
img_root = r'cat_images\1x7'
img_list = [os.path.join(img_root, p) for p in os.listdir(img_root)]        
imgs2gif(img_list, "MulitiviewC_nolabel.gif", 0.033 * 10, 0)
