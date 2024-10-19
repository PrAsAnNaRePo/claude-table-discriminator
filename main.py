import anthropic
import json
import re
import io
import base64
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

if 'data' not in st.session_state:
    st.session_state.data = json.load(open('data.json', 'r'))

if 'client' not in st.session_state:
    st.session_state.client = anthropic.Client()

def extract_code(content):
    code_blocks = re.findall(r'```html(.*?)```', content, re.DOTALL)
    return code_blocks[0].strip()


def main():
    st.title("Claude discriminator")

    idx = st.number_input("Index", min_value=1, max_value=len(st.session_state.data), value=1)

    if st.button("Discriminate"):
        img = st.session_state.data['image'][idx]
        response = st.session_state.data['response'][idx]
        tables = extract_code(response)

        col1, col2 = st.columns(2)

        with col1:
            st.image(base64.b64decode(img), caption='Uploaded Image', use_column_width=True)

        with col2:
            st.html(tables)

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

        st.write(response.content[0].text)

if __name__ == "__main__":
    main()