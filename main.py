import os, cv2, json, shutil
import numpy as np
import detectron2
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.structures import BoxMode
from matplotlib import pyplot as plt
from matplotlib.widgets import TextBox

x = []
ax = None
predictor = None
folder = "data/"
porridge_metadata = MetadataCatalog.get ("porridge_train")
OUT_FOLDER = "out/"


def get_porridge_dicts (img_dir):
    json_file = os.path.join (img_dir, "1.json")
    with open (json_file) as f:
        imgs_anns = json.load (f)

    dataset_dicts = []
    for idx, v in enumerate (imgs_anns.values ()):
        record = {}

        filename = os.path.join (img_dir, v ["filename"])
        height, width = cv2.imread (filename).shape [:2]

        record ["file_name"] = filename
        record ["image_id"] = idx
        record ["height"] = height
        record ["width"] = width

        annos = v ["regions"]
        objs = []
        for _, anno in annos.items ():
            # let it be
            assert not anno ["region_attributes"]
            anno = anno ["shape_attributes"]
            px = anno ["all_points_x"]
            py = anno ["all_points_y"]
            poly = [(x + 0.5, y + 0.5) for x, y in zip (px, py)]
            poly = [p for x in poly for p in x]

            obj = {
                "bbox": [np.min (px), np.min (py), np.max (px), np.max (py)],
                "bbox_mode": BoxMode.XYXY_ABS,
                "segmentation": [poly],
                "category_id": 0,
            }
            objs.append (obj)
        record ["annotations"] = objs
        dataset_dicts.append (record)
    return dataset_dicts


def loaddata (fname):
    global predictor, fms
    im = cv2.imread (fname)

    outputs = predictor (im)
    vals = np.zeros (20)
    for obj in outputs ["instances"].pred_masks:
        square = obj.sum ()
        if square >= 50:
            vals [min (square // 250, 19)] += 1
    return vals, outputs


def fb(text):
    try:
        fname = text
        if frameid > 0:
            visualize (fname)
    except:
        pass


def visualize (fname):
    global x, ax
    ax.clear ()
    y = loaddata (fname) [0]
    ax.set_xticks (np.arange (20), labels=x)
    p = ax.bar (np.arange (20), y)
    ax.bar_label (p, label_type="edge")
    plt.show ()


def saveimage (fname):
    v = Visualizer (frame[:, :, ::-1], metadata=porridge_metadata, scale=1.0)
    boxes = v._convert_boxes (outputs ["instances"].pred_boxes.to ("cpu"))
    masks = outputs ["instances"].get ("pred_masks")
    masks = masks.to ("cpu")
    for m in masks:
        v.draw_binary_mask (np.array(m), color = "c")
    out = v.get_output ()

    proc_img = out.get_image () [:, :, ::-1]
    cv2.imwrite (fname, proc_img)


def ProceedVideo (videoname):
    cap = cv2.VideoCapture (videoname)
    begin = int (input ("Begin from frame (indexation from 1): "))
    num = int (input ("Number of frames to proceed: "))
    end = begin + num
    k = 1
    Images = []
    while k < begin:
        ret, frame = cap.read ()
        if frame is None:  # end of video
            break
        k += 1
    AllData = []
    while k < end:
        ret, frame = cap.read ()
        if frame is None:
            break


        fname = "img" + str (k) + ".jpg"
        cv2.imwrite (folder + fname, frame)
        data, outputs = loaddata (folder + fname)
        AllData.append (data)
        """
        v = Visualizer(frame[:, :, ::-1], metadata=porridge_metadata, scale=1.0)
        #out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
        masks = outputs["instances"].get("pred_masks").to("cpu")
        for m in masks:
            v.draw_mask(m)
        v = v.get_output()
        #print(v.get_image()[:, :, ::-1])
        #cv2.imshow('Image', out.get_image()[:, :, ::-1])
        
        """
        image_file = OUT_FOLDER + "img{}.jpg".format (k)
        saveimage (image_file)

        k += 1

    SaveGistogram (begin, num, AllData)


def SaveGistogram (begin, num, fms):
    fout = open ("gistogram.txt", 'w')
    fout.write ("Number of frames: " + str (num) + '\n')
    for k in range (num):
        fout.write ("Frame: img" + str (begin + k) + ".jpg, regions: ")
        for i in range (19):
            fout.write (str (int (fms [k] [i])) + ", ")
        fout.write (str (int (fms [k] [19])) + '\n')


def ShowMarked ():
    while True:
        ifn = input ("Frame number (enter 0 to leave): ")
        if ifn == "0":
            break
        img = cv2.imread (OUT_FOLDER + "img{}.jpg".format (ifn))
        cv2.imshow ("Image", img)


def main ():
    global folder, x, ax, predictor

    cfg = get_cfg ()
    cfg.merge_from_file (model_zoo.get_config_file ("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
    cfg.TEST.DETECTIONS_PER_IMAGE = 1000
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
    cfg.MODEL.DEVICE = "cpu"
    cfg.MODEL.WEIGHTS = "model.pth"
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
    predictor = DefaultPredictor (cfg)

    try:
        shutil.rmtree (OUT_FOLDER)
        shutil.rmtree (folder)
        os.mkdir (OUT_FOLDER)
        os.mkdir (folder)

    except:
        pass

    cc = input ("Proceed single image (s) or video (v)?")
    if cc == 'v':
        vfn = input ("Video file name: ")
        ProceedVideo (vfn)

    elif cc == 's':
        sfn = input ("Image file name: ")
        im = cv2.imread (sfn)
        im = cv2.imwrite (folder + "img1.jpg", im)
        saveimage (OUT_FOLDER + "img1.jpg")
        

    vsls = input("Vilualize data on plot (y/n)?")

    if vsls == 'y':
        plt.rc ("xtick", labelsize = 5)
        fig, ax = plt.subplots ()
        ax.set_facecolor ("seashell")
        fig.set_facecolor ("floralwhite")
        fig.set_figwidth (14)
        fig.set_figheight (6)
        fig.canvas.set_window_title ("Test")

        x = ["(50; 250]"]
        for i in range (1, 20):
            x.append ("(" + str (i * 250) + "; " + str (i * 250 + 250) + "]")

        axbox = plt.axes ([0.4, 0.9, 0.2, 0.075])
        text_box = TextBox (axbox, "Image name: ", initial = "1")
        text_box.on_submit (fb)

        visualize (input ("Image file name (path included): "))

    vim = input ("Show marked images (y/n)?")
    if vim == 'y':
        ShowMarked ()


if __name__ == "__main__":
    main()