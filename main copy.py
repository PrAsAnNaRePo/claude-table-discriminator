from io import BytesIO
import anthropic
import json
import re
from PIL import Image
import base64
from dotenv import load_dotenv
import streamlit as st
import numpy as np

load_dotenv()

if 'client' not in st.session_state:
    st.session_state.client = anthropic.Client()

def extract_code(content):
    code_blocks = re.findall(r'<final>\n<table(.*?)</final>', content, re.DOTALL)
    return code_blocks

def extract_steps(content):
    steps = re.findall(r'<step>(.*?)</step>', content, re.DOTALL)
    return steps

def extract_content(content):
    mistakes = re.findall(r'<mistake>(.*?)</mistake>', content, re.DOTALL)
    score = re.findall(r'<score>(.*?)</score>', content, re.DOTALL)

    return mistakes, score[0]

def extract_breakdown(content):
    breakdown = re.findall(r'<breakdown>(.*?)</breakdown>', content, re.DOTALL)
    return breakdown

def upscale_image(base64_img, upscale_factor=1.5):
    # Decode the base64 image
    img_data = base64.b64decode(base64_img)
    img = Image.open(BytesIO(img_data))

    # Get original dimensions
    width, height = img.size

    # Calculate new dimensions (upscale)
    new_width = int(width * upscale_factor)
    new_height = int(height * upscale_factor)

    # Resize (upscale) the image
    img_resized = img.resize((new_width, new_height), Image.LANCZOS)

    # Convert resized image back to base64
    buffered = BytesIO()
    img_resized.save(buffered, format="PNG")
    upscaled_img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return upscaled_img_base64

def main():
    st.title("Claude Differentiator")

    img = st.text_area('enter base64 image')
    response = st.text_input('enter response')

    if st.button("Discriminate") and img and response:
        response = response.strip()
        # print(type(response))
        # tables = extract_code(response)
        
        _img = base64.b64decode(img)
        img_array = np.array(Image.open(BytesIO(_img)))
        st.write(img_array.shape)
        height, width, _ = img_array.shape
        upscale_factor = 1.0

        while height < 2500 and width < 2800:
            upscale_factor += 0.5
            new_width = int(width * upscale_factor)
            new_height = int(height * upscale_factor)
            
            # Update height and width for the next iteration
            height, width = new_height, new_width

        st.write(upscale_factor)
        img = upscale_image(img, upscale_factor=upscale_factor)

        normal_img = base64.b64decode(img)
        # print the size of the image
        # Print the shape of the image
        img_array = np.array(Image.open(BytesIO(normal_img)))
        st.write(f"Image shape: {img_array.shape}")

        st.image(normal_img, caption='Uploaded Image', use_column_width=True)
        
        st.html(response)
        
        msg = [
                {
                    'role': 'user',
                    'content': [
                        {
                        "type": "text",
                        "text": f"html table:\n{response}\n\nCompare the above html table with the following image."
                        },
                        {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": img,
                        },
                        }
                    ]
                }
            ]
        
        with st.spinner("loading..."):
            response = st.session_state.client.messages.create(
                model="claude-3-5-sonnet-latest",
                messages=msg,
                max_tokens=8192,
                system=open('discriminator_system_prompt copy.txt', 'r').read(),
                extra_headers={
                    'anthropic-beta': 'max-tokens-3-5-sonnet-2024-07-15'
                },
                temperature=0.1,
            )

            st.write(response.usage)

            # st.write(response.content[0].text)
            st.title("steps:")
            for i in extract_steps(response.content[0].text):
                st.write(i)

            st.title("mistakes:")
            mistakes, score = extract_content(response.content[0].text)
            st.write(mistakes[0])
            breakdown = extract_breakdown(response.content[0].text)
            st.title("mistake breakdown:")
            st.write(breakdown[0])
            st.title(f"score: {score}")
        
if __name__ == "__main__":
    main()