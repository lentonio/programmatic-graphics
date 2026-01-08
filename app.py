"""
Main application entry point with hierarchical navigation.
Organizes pages into subject groups (Maths, Chemistry, etc.)
"""

import streamlit as st

# --- Page Config (only in main app) ---
st.set_page_config(
    page_title="Diagram Generator",
    page_icon="📊",
    layout="wide"
)

# --- Define Pages ---
# Maths pages
maths_pages = [
    st.Page("pages/maths/Graphs.py", title="Function graphs", icon="📈"),
    st.Page("pages/maths/Triangles.py", title="Triangles", icon="📐"),
    st.Page("pages/maths/Circles.py", title="Circles", icon="⭕"),
    st.Page("pages/maths/Quadrilaterals.py", title="Quadrilaterals", icon="⬜"),
    st.Page("pages/maths/Number_lines.py", title="Number lines", icon="📏"),
]

# Chemistry pages
chemistry_pages = [
    st.Page("pages/chemistry/Dot_cross.py", title="Dot-and-cross", icon="⚛️"),
    st.Page("pages/chemistry/Displayed_formulae.py", title="Displayed formulae", icon="🔬"),
    st.Page("pages/chemistry/Skeletal_formulae.py", title="Skeletal formulae", icon="⛓️"),
    st.Page("pages/chemistry/Electron_shells.py", title="Electron shells", icon="🔵"),
]

# Physics pages
physics_pages = [
    st.Page("pages/physics/Vectors.py", title="Vectors", icon="➡️"),
    st.Page("pages/physics/Free_body.py", title="Free-body diagrams", icon="📦"),
    st.Page("pages/physics/Motion_graphs.py", title="Motion graphs", icon="📉"),
]

# Biology pages
biology_pages = [
    st.Page("pages/biology/Punnett_squares.py", title="Punnett squares", icon="🧬"),
    st.Page("pages/biology/Biology_graphs.py", title="Biology graphs", icon="📊"),
    st.Page("pages/biology/Transport.py", title="Transport", icon="🔄"),
]

# --- Navigation ---
pg = st.navigation({
    "Maths": maths_pages,
    "Chemistry": chemistry_pages,
    "Physics": physics_pages,
    "Biology": biology_pages,
})

pg.run()

