import anthropic
import json
import re
import pandas as pd
import base64
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

if 'data' not in st.session_state:
    st.session_state.data = json.load(open('new_data.json', 'r'))

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

def main():
    st.title("Claude Differentiator")
    st.write("Total number of images:", len(st.session_state.data['image']))
    st.info("Please try from last!")
    idx = st.number_input("idx", min_value=1, max_value=len(st.session_state.data['image']), step=1, format="%d")

    if st.button("Discriminate"):
        print("idx: ", idx)  # idx is already an integer
        img = st.session_state.data['image'][idx]
        response = st.session_state.data['response'][idx]
        tables = extract_code(response)

        st.image(base64.b64decode(img), caption='Uploaded Image', use_column_width=True)
        
        st.write(len(tables))
        if len(tables) > 0:
            st.html('<table' + tables[0])
        
            msg = [
                    {
                        'role': 'user',
                        'content': [
                            {
                            "type": "text",
                            "text": f"html table:\n{tables}\n\nCompare the above html table with the following image."
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
                    model="claude-3-5-sonnet-20240620",
                    messages=msg,
                    max_tokens=8192,
                    system=open('discriminator_system_prompt.txt', 'r').read(),
                    extra_headers={
                        'anthropic-beta': 'max-tokens-3-5-sonnet-2024-07-15'
                    },
                    temperature=0.1,
                )

                # st.write(response.content[0].text)
                st.title("here are the steps i took")
                for i in extract_steps(response.content[0].text):
                    st.write(i)

                st.title("mistakes i found")
                mistakes, score = extract_content(response.content[0].text)
                st.write(mistakes)
                st.title(f"score: {float(score)}")
        else:
            st.write("please try another")

if __name__ == "__main__":
    main()