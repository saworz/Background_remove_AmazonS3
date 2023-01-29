from features.s3_sender import S3SENDER
from features.remove_bg import remove_bg

from PIL import Image
from pathlib import Path
from io import BytesIO

import os
import streamlit as st

def save_uploadedfile(data_path: Path, uploadedfile: st.file_uploader):

    filename = uploadedfile.name

    with open(os.path.join(data_path, filename), "wb") as f:
         f.write(uploadedfile.getbuffer())
         st.success("Saved File to {}".format(data_path))


def streamlit_handling(temp_path: Path, net):

    sender = S3SENDER('mihu', 'background-remover-swz')
    bg_removed=False

    inputs_dir = temp_path / "inputs"
    st.title('Background remover')
    st.text('Upload an image and get .png without the background')

    uploaded_file = st.file_uploader('Upload file', type=["jpg", "jpeg", "png"])
    show_file = st.empty()

    if not uploaded_file:
        show_file.info("Please upload a file in the JPG, JPEG or PNG format")
        return

    if isinstance(uploaded_file, BytesIO):
        show_file.image(uploaded_file)
        filename = os.path.splitext(uploaded_file.name)[0]

    if st.button('Delete background'):
        save_uploadedfile(inputs_dir, uploaded_file)
        bg_removed = remove_bg(inputs_dir, uploaded_file.name, net)

        mask_path = str(temp_path) + "/masks/" + filename + ".png"
        result_path = str(temp_path) + "/results/" + filename + ".png" 

        mask_img = Image.open(mask_path)
        result_img = Image.open(result_path)

        st.image([mask_img, result_img], width=350, caption=["Generated mask", "Final result"])
        st.text(str(temp_path) + "/masks/" + filename + ".png")

        st.session_state.mask_path = mask_path
        st.session_state.result_path = result_path

    if st.button('Upload image', disabled=not bg_removed):
        sender.send_image(inputs_dir / uploaded_file.name, uploaded_file.name)
        sender.send_image(st.session_state.mask_path, filename + "_mask.png")
        sender.send_image(st.session_state.result_path, filename + "_result.png")