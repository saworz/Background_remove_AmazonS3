from front.streamlit_handling import streamlit_handling
from features.remove_bg import remove_bg
from pathlib import Path
import os
import torch
from model.u2net import U2NET


def main():
    temp_path = Path(__file__).parent / "data" / "temp"
    currentDir = os.path.dirname(__file__)

    print("---Loading Model---")
    model_name = 'u2net'
    model_dir = os.path.join(Path(currentDir).parent, 'saved_models',
                            model_name, model_name + '.pth')

    net = U2NET(3, 1)

    net.load_state_dict(torch.load(model_dir, map_location='cpu'))
    print("Model loaded on cpu")
    streamlit_handling(temp_path, net)
    
    

if __name__ == '__main__':
    main()