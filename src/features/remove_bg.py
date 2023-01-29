from PIL import Image
from skimage import io, transform
from pathlib import Path

import os
import cv2
import numpy as np
import torch


def save_output(image_name: str, output_name: str, pred: torch.tensor, d_dir: Path, type: str):

    predict = pred.squeeze()
    predict_np = predict.cpu().data.numpy()

    img = Image.fromarray(predict_np*255).convert('RGB')
    image_in = io.imread(image_name)
    image_out = img.resize((image_in.shape[1], image_in.shape[0]))

    if type == 'image':
        # Make and apply mask
        mask = np.array(image_out)[:, :, 0]
        mask = np.expand_dims(mask, axis=2)
        image_out = np.concatenate((image_in, mask), axis=2)
        image_out = Image.fromarray(image_out, 'RGBA')

    image_out.save(d_dir / output_name)


def remove_bg(imagePath: Path, filename: str, net: torch.nn.Sequential) -> bool:

    results_dir = Path(__file__).parent.parent / "data" / "temp" / "results"
    masks_dir = Path(__file__).parent.parent / "data" / "temp" / "masks"

    with open(imagePath / filename, "rb") as image:
        f = image.read()
        img = bytearray(f)

    nparr = np.frombuffer(img, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    image = transform.resize(img, (320, 320), mode='constant')

    tmpImg = np.zeros((image.shape[0], image.shape[1], 3))

    tmpImg[:, :, 0] = (image[:, :, 0]-0.485)/0.229
    tmpImg[:, :, 1] = (image[:, :, 1]-0.456)/0.224
    tmpImg[:, :, 2] = (image[:, :, 2]-0.406)/0.225

    tmpImg = tmpImg.transpose((2, 0, 1))
    tmpImg = np.expand_dims(tmpImg, 0)
    image = torch.from_numpy(tmpImg)

    image = image.type(torch.FloatTensor)
    image = torch.autograd.Variable(image)
    
    d1, d2, d3, d4, d5, d6, d7 = net(image)
    pred = d1[:, 0, :, :]
    pred_max = torch.max(pred)
    pred_min = torch.min(pred)
    pred = (pred-pred_min)/(pred_max-pred_min)

    save_output(str(imagePath / filename), os.path.splitext(filename)[0] +
                '.png', pred, results_dir, 'image')
    save_output(str(imagePath / filename), os.path.splitext(filename)[0] +
                '.png', pred, masks_dir, 'mask')
    return True