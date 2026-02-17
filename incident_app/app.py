import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# ---------- DATABASE ----------
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    product TEXT,
    batch_no TEXT,
    department TEXT,
    category TEXT,
    severity TEXT,
    description TEXT,
    reporter TEXT,
    status TEXT,
    image_path TEXT
)
""")
conn.commit()

# ---------- FUNCTIONS ----------
def add_incident(data):
    c.execute("""
        INSERT INTO incidents 
        (date, product, batch_no, department, category, severity, description, reporter, status, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()

def get_incidents():
    return pd.read_sql("SELECT * FROM incidents", conn)

def update_status(id, status):
    c.execute("UPDATE incidents SET status=? WHERE id=?", (status, id))
    conn.commit()

# ---------- UI ----------
st.title("Product Quality Incident App")

menu = st.sidebar.selectbox(
    "Menu",
    ["Submit Incident", "View Incidents", "Dashboard"]
)

# ---------- SUBMIT ----------
if menu == "Submit Incident":
    st.header("Report New Incident")

    product = st.text_input("Product Name")
    batch = st.text_input("Batch Number")
    dept = st.selectbox("Department",
        ["Production", "QA", "Warehouse", "Maintenance", "Utility"]
    )
    category = st.selectbox("Category",
        ["Product Defect","Process Deviation","Personnel Issue",
         "Equipment Failure","Facility Risk","GMP/Hygiene","Others"]
    )
    severity = st.selectbox("Severity", ["Low","Medium","High"])
    desc = st.text_area("Description")
    reporter = st.text_input("Reporter Name")

    img = st.file_uploader("Upload Image", type=["jpg","png","jpeg"])

    if st.button("Submit"):
        img_path = ""
        if img:
            os.makedirs("images", exist_ok=True)
            img_path = f"images/{img.name}"
            with open(img_path, "wb") as f:
                f.write(img.getbuffer())

        data = (
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            product, batch, dept, category,
            severity, desc, reporter,
            "New", img_path
        )
        add_incident(data)
        st.success("Incident Submitted!")

# ---------- VIEW ----------
elif menu == "View Incidents":
    st.header("All Incidents")

    df = get_incidents()

    if not df.empty:
        st.dataframe(df)

        id_select = st.number_input("Incident ID to Update", step=1)
        new_status = st.selectbox(
            "Update Status",
            ["New","Under Review","Closed"]
        )

        if st.button("Update Status"):
            update_status(id_select, new_status)
            st.success("Status Updated")
    else:
        st.info("No incidents yet.")

# ---------- DASHBOARD ----------
elif menu == "Dashboard":
    st.header("Incident Dashboard")

    df = get_incidents()

    if not df.empty:
        st.subheader("By Category")
        st.bar_chart(df["category"].value_counts())

        st.subheader("By Department")
        st.bar_chart(df["department"].value_counts())

        st.subheader("Status")
        st.bar_chart(df["status"].value_counts())
    else:
        st.info("No data yet.")
