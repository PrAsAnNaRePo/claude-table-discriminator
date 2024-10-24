from io import BytesIO
import anthropic
import json
import re
from PIL import Image
import base64
from dotenv import load_dotenv
import streamlit as st

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
        img = upscale_image(img, upscale_factor=1.5)
        st.image(base64.b64decode(img), caption='Uploaded Image', use_column_width=True)
        
        st.html(response)

        # st.write(len(tables))
        # if len(tables) > 0:
        #     st.html('<table' + tables[0])
        
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
                system=open('discriminator_system_prompt.txt', 'r').read(),
                extra_headers={
                    'anthropic-beta': 'max-tokens-3-5-sonnet-2024-07-15'
                },
                temperature=0.1,
            )

            st.write(response.usage)

            # st.write(response.content[0].text)
            st.title("here are the steps i took")
            for i in extract_steps(response.content[0].text):
                st.write(i)

            st.title("mistakes i found")
            mistakes, score = extract_content(response.content[0].text)
            st.write(mistakes)
            st.title(f"score: {score}")
        # else:
        #     st.write("please try another")

if __name__ == "__main__":
    main()