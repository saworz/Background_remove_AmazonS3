from front.streamlit_handling import streamlit_handling
from model.u2net import U2NET

from pathlib import Path
from typing import Tuple
import os
import torch
import streamlit as st


@st.cache
def bind_socket() -> Tuple[Path, torch.nn.Sequential]:
    # Load model's weights only on the first run

    temp_path = Path(__file__).parent / "data" / "temp"
    currentDir = os.path.dirname(__file__)

    print("Loading model...")
    model_name = 'u2net'
    model_dir = os.path.join(Path(currentDir).parent, 'saved_models',
                            model_name, model_name + '.pth')

    net = U2NET(3, 1)
    net.load_state_dict(torch.load(model_dir, map_location='cpu'))
    
    print("Model loaded on cpu.")
    return temp_path, net


def main():
    temp_path, net = bind_socket()
    streamlit_handling(temp_path, net)
    
    
if __name__ == '__main__':
    main()