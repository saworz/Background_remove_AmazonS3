from front.streamlit_handling import streamlit_handling
from features.remove_bg import remove_bg
from pathlib import Path
import os
import torch
from model.u2net import U2NET

def main():
    data_path = Path(__file__).parent.parent / "data" / "uploaded"
    currentDir = os.path.dirname(__file__)
    streamlit_handling(data_path)

    print("---Loading Model---")
    model_name = 'u2net'
    model_dir = os.path.join(Path(currentDir).parent, 'saved_models',
                            model_name, model_name + '.pth')

    net = U2NET(3, 1)
    if torch.cuda.is_available():
        net.load_state_dict(torch.load(model_dir))
        net.cuda()
        print("Model loaded on cuda device")
    else:
        net.load_state_dict(torch.load(model_dir, map_location='cpu'))
        print("Model loaded on cpu")

    remove_bg(data_path / "2023_01_23-07_30_39_PM.jpg", currentDir, net)

if __name__ == '__main__':
    main()