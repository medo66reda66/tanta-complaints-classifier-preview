
import streamlit as st
from pathlib import Path
import uuid
from datetime import datetime
from storage import initialize_files, save_complaint
from agent_service import ComplaintService
from priority_reasoning import prioritize


@st.cache_resource
def get_service():
    return ComplaintService()


initialize_files()
st.set_page_config(
    page_title="Tanta University Complaints",
    page_icon="🎓",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background-color: #F8FAFC;
    font-family: sans-serif;
}

.main-title {
    color: #0F172A;
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 5px;
    margin-top: 10px;
}

.subtitle {
    color: #0EA5E9;
    font-size: 16px;
    font-weight: 500;
}

.section-header {
    color: #0F172A;
    font-size: 20px;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 15px;
    padding-bottom: 6px;
    border-bottom: 2px solid #E2E8F0;
}

div[data-testid="stForm"] {
    background-color: #FFFFFF;
    padding: 28px;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
    border: 1px solid #E2E8F0;
}

.form-sub-header {
    color: #334155;
    font-size: 16px;
    font-weight: 600;
    margin-top: 16px;
    margin-bottom: 10px;
}

div.stButton > button, div.stFormSubmitButton > button {
    background-color: #0EA5E9;
    color: #FFFFFF;
    border-radius: 8px;
    border: none;
    width: 100%;
    height: 48px;
    font-size: 16px;
    font-weight: 600;
    box-shadow: 0 2px 6px rgba(14, 165, 233, 0.25);
    transition: all 0.2s ease;
}

div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    background-color: #0284C7;
    color: #FFFFFF;
    box-shadow: 0 4px 10px rgba(14, 165, 233, 0.35);
    transform: translateY(-1px);
}

div[data-testid="stTextInput"],
div[data-testid="stSelectbox"],
div[data-testid="stTextArea"] {
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

logo_path = Path("tanta_logo.png")
_b64 = Path("tanta_logo_b64.txt")
if not logo_path.exists() and _b64.exists():
    import base64
    logo_path.write_bytes(base64.b64decode(_b64.read_text().strip()))

col1, col2 = st.columns([1, 4])

with col1:
    if logo_path.exists():
        st.image(str(logo_path), width=90)
    else:
        st.markdown("## 🎓")

with col2:
    st.markdown('<div class="main-title">Tanta University Complaints</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Smart Complaint Management System</div>', unsafe_allow_html=True)

st.info("🧪 Demo version: please do NOT enter real personal data. Submitted complaints are stored temporarily and are erased whenever the app restarts.")

st.divider()

tanta_faculties = [
    "Select your college",
    "Faculty of Computers and Information",
    "Faculty of Engineering",
    "Faculty of Medicine",
    "Faculty of Science",
    "Faculty of Commerce",
    "Faculty of Arts",
    "Faculty of Law",
    "Faculty of Agriculture",
    "Faculty of Dentistry",
    "Faculty of Pharmacy",
    "Faculty of Education",
    "Faculty of Specific Education",
    "Faculty of Nursing",
    "Faculty of Physical Education",
    "Faculty of Veterinary Medicine",
    "Other"
]

with st.form("complaint_form"):
    st.markdown('<div class="section-header">Submit Your Complaint</div>', unsafe_allow_html=True)

    st.markdown('<div class="form-sub-header">Student Information</div>', unsafe_allow_html=True)
    student_name = st.text_input("Full Name", placeholder="Enter your full name")
    student_id = st.text_input("University ID", placeholder="Enter your student ID")
    email = st.text_input("University Email", placeholder="student@tanta.edu.eg")

    college = st.selectbox("College", tanta_faculties)

    st.markdown('<div class="form-sub-header">Complaint Information</div>', unsafe_allow_html=True)
    complaint_type = st.selectbox(
        "Complaint Category",
        [
            "Academic",
            "Administrative",
            "Technical",
            "Facilities",
            "Other"
        ]
    )

    complaint_title = st.text_input("Complaint Title", placeholder="Brief summary of the issue")

    complaint_details = st.text_area(
        "Complaint Details",
        placeholder="Please describe your complaint in detail...",
        height=140
    )

    attachment = st.file_uploader(
        "Attach a File (Optional)",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    submitted = st.form_submit_button("Submit Complaint")

    if submitted:
        if not student_name or not student_id or not complaint_details:
            st.warning("Please fill in your name, university ID, and complaint details.")

        elif college == "Select your college":
            st.warning("Please select your college.")

        else:
            complaint_id = f"TC-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"

            full_text = f"{complaint_title} {complaint_details}".strip()
            try:
                ai_category, _ = get_service().classify(full_text)
                result = prioritize(full_text, ai_category)
                priority = result["priority"]
                reasoning = " | ".join(result["reasons"])
            except Exception as exc:
                ai_category, priority, reasoning = "", "", f"Auto-analysis failed: {exc}"

            complaint = {
                "complaint_id": complaint_id,
                "student_name": student_name,
                "student_id": student_id,
                "student_email": email,
                "college": college,
                "complaint_type": complaint_type,
                "title": complaint_title,
                "details": complaint_details,
                "status": "Pending",
                "ai_category": ai_category,
                "priority": priority,
                "reasoning": reasoning,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            save_complaint(complaint)

            st.success("Your complaint has been submitted successfully!")
            st.info(f"Your Complaint ID is: {complaint_id}")
            st.caption(f"Classified as: {ai_category or 'N/A'} | Priority: {priority or 'N/A'}")
            st.info("Please save this number to track your complaint.").write("")
    
