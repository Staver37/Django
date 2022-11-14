import torch, torch.nn as nn
from PIL import Image,ImageOps
import numpy as np

def imageToTensor(file_name):
      img = Image.open("/Users/adrian/Desktop/PY-PROJECTS/Django/e-shop/shop/static/uploaded/product_images/{file_name}")
      img = img.crop((0,0,500,500))
      img = ImageOps.grayscale(img)
      img_matrix= np.array(img)
      img_tensor = torch.from_numpy(img_matrix).type(torch.FloatTensor).view(1,500,500)
      return img_tensor


def validateImageQuality(file_name):
    model = nn.Sequential(
        nn.Conv2d(in_channels=1,out_channels=96,kernel_size=(10,10), stride = (20,20)), 
        nn.Flatten(start_dim=0), 
        nn.Linear(in_features=40000, out_features=2),                               
    )

    
    model.load_state_dict(torch.load('/Users/adrian/Desktop/PY-PROJECTS/Django/e-shop/shop/ai-models/image-quality-detector-64-20x20-1000-x-images'))
    model.eval()

    x_tensor= imageToTensor(file_name)
    y_predicted = model(x_tensor)
    valid = torch.argmax(y_predicted)
    print(">>>>>> valid ?",  valid)
    return valid