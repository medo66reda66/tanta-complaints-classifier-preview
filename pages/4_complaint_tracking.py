import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Complaint Tracking",
    page_icon="🔎",
    layout="wide"
)

# =========================
# Page Design
# =========================

st.markdown("""
<style>
.stApp {
    background-color: #F5F8FC;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1150px;
}

.main-header {
    background: linear-gradient(120deg, #234E70, #397BA8);
    padding: 30px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}

.main-header h1 {
    color: white;
    margin-bottom: 8px;
    font-size: 32px;
}

.main-header p {
    color: #E6F1FA;
    font-size: 15px;
}

.section-card {
    background: white;
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #E5ECF3;
    margin-bottom: 18px;
}

.info-label {
    color: #718096;
    font-size: 13px;
    margin-bottom: 5px;
}

.info-value {
    color: #244B70;
    font-size: 17px;
    font-weight: 600;
}

.status-box {
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    font-size: 18px;
    font-weight: bold;
}

.update-card {
    background: #F8FAFD;
    border-left: 4px solid #397BA8;
    padding: 16px;
    border-radius: 10px;
    margin-bottom: 12px;
}

div.stButton > button {
    background-color: #2F6F9F;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 25px;
    font-weight: 600;
}

div.stButton > button:hover {
    background-color: #234E70;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# =========================
# File Paths
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COMPLAINTS_FILE = os.path.join(BASE_DIR, "complaints.csv")
UPDATES_FILE = os.path.join(BASE_DIR, "complaint_updates.csv")


# =========================
# Load Data
# =========================

def load_data(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()

    try:
        return pd.read_csv(file_path, dtype=str).fillna("")
    except Exception:
        return pd.DataFrame()


# =========================
# Status Colors
# =========================

STATUS_COLORS = {
    "Pending": ("#FFF4D6", "#9A6700"),
    "Under Review": ("#E8F1FF", "#245B9E"),
    "In Progress": ("#FFF0DF", "#B76513"),
    "Resolved": ("#E3F7EC", "#217A48"),
    "Rejected": ("#FCE8E8", "#B42318")
}

STATUS_STEPS = [
    "Pending",
    "Under Review",
    "In Progress",
    "Resolved"
]


# =========================
# Header
# =========================

st.markdown("""
<div class="main-header">
    <h1>🔎 Complaint Tracking</h1>
    <p>Follow your complaint and stay updated with its latest status.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="color:#52677D; font-size:15px; margin-bottom:15px;">
    Enter your Complaint ID below to view your complaint details and updates.
</div>
""", unsafe_allow_html=True)


# =========================
# Search Complaint
# =========================

complaints_df = load_data(COMPLAINTS_FILE)
updates_df = load_data(UPDATES_FILE)

with st.container(border=True):
    st.markdown("### 🔍 Find Your Complaint")

    complaint_id = st.text_input(
        "Complaint ID",
        placeholder="Enter your Complaint ID (e.g. CMP-2026-001)"
    ).strip()

    search_button = st.button(
        "Track My Complaint",
        use_container_width=True
    )


# =========================
# Search Results
# =========================

if search_button:

    if not complaint_id:
        st.warning("Please enter your Complaint ID.")

    elif complaints_df.empty:
        st.error("No complaint records were found.")

    elif "complaint_id" not in complaints_df.columns:
        st.error("The complaint file does not have the expected ID column.")

    else:

        complaint_match = complaints_df[
            complaints_df["complaint_id"].astype(str).str.strip().str.lower()
            == complaint_id.lower()
        ]

        if complaint_match.empty:
            st.error("Complaint ID not found. Please check your ID and try again.")

        else:

            complaint = complaint_match.iloc[0]

            current_status = complaint.get("status", "Pending").strip()

            if not current_status:
                current_status = "Pending"

            bg_color, text_color = STATUS_COLORS.get(
                current_status,
                ("#EDF2F7", "#40566D")
            )

            st.markdown("---")
            st.markdown("## 📋 Complaint Details")

            # =========================
            # Complaint Information
            # =========================

            st.markdown('<div class="section-card">', unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f"""
                    <div class="info-label">Complaint ID</div>
                    <div class="info-value">{complaint.get('complaint_id', '')}</div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div class="info-label">College</div>
                    <div class="info-value">{complaint.get('college', 'N/A')}</div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"""
                    <div class="info-label">Complaint Type</div>
                    <div class="info-value">{complaint.get('complaint_type', 'N/A')}</div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div class="info-label">Submission Date</div>
                    <div class="info-value">{complaint.get('created_at', 'N/A')}</div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="info-label">Complaint Title</div>
                <div class="info-value">{complaint.get('title', 'N/A')}</div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="info-label">Complaint Details</div>
                <div style="color:#40566D; font-size:15px;">
                    {complaint.get('details', 'N/A')}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown('</div>', unsafe_allow_html=True)

            # =========================
            # Current Status
            # =========================

            st.markdown("### 📌 Current Status")

            st.markdown(
                f"""
                <div class="status-box"
                     style="background-color:{bg_color}; color:{text_color};">
                    {current_status}
                </div>
                """,
                unsafe_allow_html=True
            )

            # =========================
            # Progress Timeline
            # =========================

            st.markdown("### 📈 Complaint Progress")

            if current_status in STATUS_STEPS:
                current_index = STATUS_STEPS.index(current_status)

                for index, step in enumerate(STATUS_STEPS):

                    if index < current_index:
                        icon = "🟢"
                        color = "#217A48"
                        message = "Completed"

                    elif index == current_index:
                        icon = "🔵"
                        color = "#245B9E"
                        message = "Current Status"

                    else:
                        icon = "⚪"
                        color = "#A0AEC0"
                        message = "Waiting"

                    st.markdown(
                        f"""
                        <div style="
                            background:white;
                            padding:14px;
                            border-radius:12px;
                            margin-bottom:9px;
                            border:1px solid #E5ECF3;
                        ">
                            <span style="font-size:19px;">{icon}</span>
                            <b style="color:{color}; margin-left:8px;">
                                {step}
                            </b>
                            <span style="float:right; color:#718096; font-size:13px;">
                                {message}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            elif current_status == "Rejected":
                st.error("This complaint has been rejected.")

            else:
                st.info("The current status is not recognized in the progress timeline.")

            # =========================
            # Admin Updates
            # =========================

            st.markdown("### 💬 Updates from Administration")

            if not updates_df.empty and "complaint_id" in updates_df.columns:

                complaint_updates = updates_df[
                    updates_df["complaint_id"].astype(str).str.strip().str.lower()
                    == complaint_id.lower()
                ].copy()

                if not complaint_updates.empty:

                    if "updated_at" in complaint_updates.columns:
                        complaint_updates = complaint_updates.sort_values(
                            by="updated_at",
                            ascending=False
                        )

                    for _, update in complaint_updates.iterrows():

                        update_status = update.get("status", "Update")
                        admin_note = update.get("admin_note", "")
                        update_date = update.get("updated_at", "")

                        st.markdown(
                            f"""
                            <div class="update-card">
                                <div style="color:#244B70; font-weight:bold;">
                                    📌 {update_status}
                                </div>
                                <div style="color:#40566D; margin-top:8px;">
                                    {admin_note if admin_note else "No additional note."}
                                </div>
                                <div style="color:#8293A3; font-size:12px; margin-top:10px;">
                                    🕒 {update_date}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                else:
                    st.info("There are no additional updates from the administration yet.")

            else:
                st.info("There are no additional updates from the administration yet.")

            # =========================
            # Final Message
            # =========================

            if current_status == "Resolved":
                st.success("Your complaint has been resolved. Thank you for your patience!")

            elif current_status == "Rejected":
                st.warning("Your complaint was rejected. Please review the administration updates.")

            else:
                st.info("Your complaint is being followed up. Please check again later for new updates.")

else:
    st.markdown("""
    <div style="
        background:#EAF3FA;
        padding:20px;
        border-radius:14px;
        margin-top:20px;
        color:#315B7D;
    ">
        <b>💡 Helpful Tip</b>
        <p style="margin-bottom:0;">
            Keep your Complaint ID safe. You will need it whenever you want to track your complaint.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<div style="text-align:center; color:#8293A3; font-size:13px;">
    Smart Complaint Management System | Tanta University
</div>
""", unsafe_allow_html=True)
