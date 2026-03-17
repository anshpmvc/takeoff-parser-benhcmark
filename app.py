import streamlit as st
import json
from PIL import Image, ImageDraw
from parsers.roboflow_parser import RoboflowParser
from parsers.pdf_to_images import PDFToImages

st.set_page_config(page_title="Takeoff Parser", layout="wide")
st.title("Blueprint Takeoff Extractor")

uploaded = st.file_uploader("Upload a blueprint PDF", type=["pdf"])

if uploaded:
    with open("data/samples/uploaded.pdf", "wb") as f:
        f.write(uploaded.read())

    with st.spinner("Converting PDF to images..."):
        converter = PDFToImages(dpi=300)
        pages = converter.convert("data/samples/uploaded.pdf")

    page_num = st.slider("Select page", 1, len(pages), 1)
    image_path = pages[page_num - 1]

    col1, col2 = st.columns([2, 1])

    with st.spinner("Running detection..."):
        parser = RoboflowParser()
        result = parser.extract_takeoff(image_path)

    with col1:
        st.subheader("Blueprint")
        img = Image.open(image_path).convert("RGB")
        st.image(img, use_container_width=True)

    with col2:
        st.subheader(f"Detected Items ({len(result['line_items'])})")
        st.caption(f"Runtime: {result['runtime_ms']}ms")

        if result["line_items"]:
            for item in result["line_items"]:
                conf = item["confidence"]
                color = "green" if conf > 0.7 else "orange" if conf > 0.5 else "red"
                st.markdown(f"""
**{item['material']}**
- Location: `{item['location']}`
- Confidence: :{color}[{conf:.0%}]
- Source: `{item['source']}`
---""")
        else:
            st.info("No items detected on this page.")

        st.subheader("Raw JSON")
        st.json(result)
