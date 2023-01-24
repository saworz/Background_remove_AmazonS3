import numpy as np
from PIL import Image
import io
import os
import cv2
import uuid
from skimage import transform
import torch

def save_output(image_name, output_name, pred, d_dir, type):
    predict = pred
    predict = predict.squeeze()
    predict_np = predict.cpu().data.numpy()
    im = Image.fromarray(predict_np*255).convert('RGB')
    image = io.imread(image_name)
    imo = im.resize((image.shape[1], image.shape[0]))
    pb_np = np.array(imo)
    if type == 'image':
        # Make and apply mask
        mask = pb_np[:, :, 0]
        mask = np.expand_dims(mask, axis=2)
        imo = np.concatenate((image, mask), axis=2)
        imo = Image.fromarray(imo, 'RGBA')

    imo.save(d_dir+output_name)
# Remove Background From Image (Generate Mask, and Final Results)

def remove_bg(imagePath, currentDir, net):
    inputs_dir = os.path.join(currentDir, 'static/inputs/')
    results_dir = os.path.join(currentDir, 'static/results/')
    masks_dir = os.path.join(currentDir, 'static/masks/')

    # convert string of image data to uint8
    with open(imagePath, "rb") as image:
        f = image.read()
        img = bytearray(f)

    nparr = np.frombuffer(img, np.uint8)

    if len(nparr) == 0:
        return '---Empty image---'

    # decode image
    try:
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except:
        # build a response dict to send back to client
        return "---Empty image---"

    # save image to inputs
    unique_filename = str(uuid.uuid4())
    cv2.imwrite(inputs_dir+unique_filename+'.jpg', img)

    # processing
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

    print(net)
    
    d1, d2, d3, d4, d5, d6, d7 = net(image)
    pred = d1[:, 0, :, :]
    ma = torch.max(pred)
    mi = torch.min(pred)
    dn = (pred-mi)/(ma-mi)
    pred = dn

    save_output(inputs_dir+unique_filename+'.jpg', unique_filename +
                '.png', pred, results_dir, 'image')
    save_output(inputs_dir+unique_filename+'.jpg', unique_filename +
                '.png', pred, masks_dir, 'mask')
    return "---Success---"