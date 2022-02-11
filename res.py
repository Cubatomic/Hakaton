import cv2
import numpy as np
import os
import detectron2
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
#from detectron2.utils.visualizer import Visualizer
#from detectron2.data import MetadataCatalog, DatasetCatalog
#from detectron2.structures import BoxMode
#from detectron2.utils.visualizer import ColorMode
from matplotlib import pyplot as plt
from matplotlib.widgets import TextBox

x = []
ax = None
predictor = None

def loadframe (fname):
    global predictor

    im = cv2.imread ("data/" + fname)
    outputs = predictor (im)
    #v = Visualizer (im [:, :, ::-1], metadata = porridge_metadata, scale = 1.0)
    #out = v.draw_instance_predictions (outputs ["instances"].to ("cpu"))
    #cv2_imshow (out.get_image () [:, :, ::-1])
    return np.random.randint (1, 20, size = 20)
    #return outputs ["pred_keypoint"]


def fb (text):
    try:
        frameid = int (text)
        visualize (frameid)
    except:
        pass


def visualize (frameid):
    global x, ax

    ax.clear ()
    fname = "img" + str (frameid) + ".jpg"
    y = loadframe (fname)
    ax.set_xticks (np.arange (20), labels = x)
    p = ax.bar (np.arange (20), y)
    ax.bar_label (p, label_type = "edge")
    plt.show ()


def proceed ():
    print ("brr")


def main ():
    global x, ax, predictor
    
    vfn = input ("Video file name: ")
    cap = cv2.VideoCapture (vfn)
    k = 1
    while True:
        ret, frame = cap.read ()
        if frame is None:
            break
        tk = str (k)
        cv2.imwrite ("data/img" + tk + ".jpg", frame)
        print (k)
        k += 1

    cfg.MODEL.WEIGHTS = "model.pth"
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
    predictor = DefaultPredictor (cfg)

    plt.rc ("xtick", labelsize = 5)
    fig, ax = plt.subplots ()
    ax.set_facecolor ("seashell")
    fig.set_facecolor ("floralwhite")
    fig.set_figwidth (14)
    fig.set_figheight (6)
    fig.canvas.set_window_title ("Test")
    
    x = ["(50; 250]"]
    for i in range (1, 20):
        x.append ("(" + str (i*250) + "; " + str (i*250 + 250) + "]")

    axbox = plt.axes ([0.4, 0.9, 0.2, 0.075])
    text_box = TextBox (axbox, "Frame: ", initial = "0")
    text_box.on_submit (fb)
    
    visualize (0)


if __name__ == "__main__":
    main ()