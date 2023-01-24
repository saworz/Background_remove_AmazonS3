from features.s3_sender import S3SENDER
from datetime import datetime

from pathlib import Path
import os
import streamlit as st
from io import BytesIO

def save_uploadedfile(data_path: Path, uploadedfile: st.file_uploader) -> str:

    file = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    extension = os.path.splitext(uploadedfile.name)[1]
    filename = file + extension

    with open(os.path.join(data_path, filename), "wb") as f:
         f.write(uploadedfile.getbuffer())
         st.success("Saved File:{} to {}".format(filename, data_path))

    return filename


def streamlit_handling(data_path: Path):

    aws_access_key_id = 'AKIATHVU5KJLC6ZXDL7Z'
    aws_secret_access_key = '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'
    sender = S3SENDER(aws_access_key_id, aws_secret_access_key, 'mihu', 'background-remover-swz')

    st.title('Background remover')
    st.text('Upload an image and get .png without the background')

    uploaded_file = st.file_uploader('Upload file', type=["jpg", "jpeg", "png"])
    show_file = st.empty()

    if not uploaded_file:
        show_file.info("Please upload a file in the JPG, JPEG or PNG format")
        return

    if isinstance(uploaded_file, BytesIO):
        show_file.image(uploaded_file)

    if st.button('Upload an image'):
        filename = save_uploadedfile(data_path, uploaded_file)
        sender.send_image(data_path / filename, filename)