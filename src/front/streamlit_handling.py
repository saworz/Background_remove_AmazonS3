from features.s3_sender import S3SENDER
from features.remove_bg import remove_bg

import PIL
from PIL import Image
from pathlib import Path
from io import BytesIO

import os
import streamlit as st
import boto3
import json

def save_uploadedfile(data_path: Path, uploadedfile: st.file_uploader):

    filename = uploadedfile.name

    with open(os.path.join(data_path, filename), "wb") as f:
         f.write(uploadedfile.getbuffer())


def streamlit_handling(temp_path: Path, net):

    sender = S3SENDER('mihu', 'background-remover-swz')
    lambda_client = boto3.client('lambda')
    bg_removed=False

    inputs_dir = temp_path / "inputs"
    title = '<p style="text-align: center; font-family:Arial; color:White; font-size: 60px;">Background remover</p>'
    st.markdown(title, unsafe_allow_html=True)
    st.markdown("""---""")

    subtitle_1 = '<p style="text-align: center; font-family:Arial; color:White; font-size: 30px;">Press to read all files in the Amazon S3 bucket service.</p>'
    st.markdown(subtitle_1, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
    col_dict = {}
    col_dict['1'] = col1
    col_dict['3'] = col3
    col_dict['5'] = col5

    with col3 :
        if st.button('Read data from S3'):
            response = lambda_client.invoke(FunctionName='get_list_of_items', 
                        InvocationType='RequestResponse')
            json_string = response['Payload'].read().decode()
            files_list = json.loads(json_string)["body"]
            st.session_state.files_list = files_list
            st.session_state.display_results = True

    col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
    col_dict = {}
    col_dict['1'] = col1
    col_dict['3'] = col3
    col_dict['5'] = col5

    try:
        if st.session_state.display_results:
            column=1

            for i, item in enumerate(st.session_state.files_list):
                with col_dict[str(column)]:
                    if not "_mask.png" in item and not "_result.png" in item:
                        st.markdown("- " + item + ",  " + os.path.splitext(item)[0] + "_mask.png" + ",  " + os.path.splitext(item)[0] + "_result.png")
                        column+=2
                        if column==7:
                            column=1
    except:
        pass

    st.markdown("""---""")
    subtitle_2 = '<p style="text-align: center; font-family:Arial; color:White; font-size: 30px;">Enter filename and two diagonal positions of the image to be cut.</p>'
    st.markdown(subtitle_2, unsafe_allow_html=True)

    file_request = st.text_input(label="Enter file name")

    col1, col2, col3, col4 = st.columns([1,1,1,1])

    with col2:
        UpLeft = st.number_input(label="Up left", min_value=0, max_value=9999)
    with col3:
        RightDown = st.number_input(label="Right down", min_value=0, max_value=9999)
    
    col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])

    with col3:
        if st.button('Crop and display selected image'):
            response = lambda_client.invoke(FunctionName='crop_images', 
                        InvocationType='RequestResponse',
                        Payload=json.dumps(file_request))
            json_string = response['Payload'].read().decode()
            response = json.loads(json_string)["body"]
            print(response)

    st.markdown("""---""")
    subtitle_3 = '<p style="text-align: center; font-family:Arial; color:White; font-size: 30px;">Upload an image and get .png without the background.</p>'
    st.markdown(subtitle_3, unsafe_allow_html=True)

    uploaded_file = st.file_uploader('Upload file', type=["jpg", "jpeg", "png"])
    show_file = st.empty()

    if not uploaded_file:
        show_file.info("Please upload a file in the JPG, JPEG or PNG format")
        return

    if isinstance(uploaded_file, BytesIO):
        show_file.image(uploaded_file)
        filename = os.path.splitext(uploaded_file.name)[0]

    threshold = st.slider("Set threshold", min_value=0.05, max_value=0.99, value=0.5)

    if st.button('Delete background'):
        save_uploadedfile(inputs_dir, uploaded_file)
        bg_removed = remove_bg(inputs_dir, uploaded_file.name, threshold, net)

        mask_path = str(temp_path) + "/masks/" + filename + ".png"
        result_path = str(temp_path) + "/results/" + filename + ".png" 

        mask_img = Image.open(mask_path)
        result_img = Image.open(result_path)

        st.image([mask_img, result_img], width=350, caption=["Generated mask", "Final result"])

        st.session_state.mask_path = mask_path
        st.session_state.result_path = result_path

    if st.button('Upload image', disabled=not bg_removed):
        sender.send_image(inputs_dir / uploaded_file.name, uploaded_file.name)
        sender.send_image(st.session_state.mask_path, filename + "_mask.png")
        sender.send_image(st.session_state.result_path, filename + "_result.png")

        os.remove(inputs_dir / uploaded_file.name)
        os.remove(st.session_state.mask_path)
        os.remove(st.session_state.result_path)

        show_file = st.empty()
        st.text("Files successfully uploaded to S3 bucket!")
