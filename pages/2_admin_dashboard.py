import streamlit as st
import csv
from pathlib import Path
from storage import initialize_files, add_complaint_update

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="🎓",
    layout="wide"
)

from admin_gate import require_admin
require_admin()


initialize_files()

COMPLAINTS_FILE = Path("complaints.csv")

# --------------------------------------------------
# CUSTOM DESIGN
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #F4F7FB;
    color: #1E293B;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.main-header {
    font-size: 30px;
    font-weight: 800;
    color: #163A5F;
    margin-bottom: 4px;
}

.sub-header {
    color: #718096;
    font-size: 15px;
    margin-bottom: 20px;
}

.section-title {
    color: #163A5F;
    font-size: 21px;
    font-weight: 700;
    margin-top: 15px;
    margin-bottom: 12px;
}

div[data-testid="stMetric"] {
    background-color: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
}

div[data-testid="stMetricLabel"] {
    color: #64748B;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #163A5F;
    font-weight: 800;
}

div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] {
    border-radius: 9px;
}

div[data-testid="stForm"] {
    background-color: white;
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #E2E8F0;
}

div.stButton > button,
div.stFormSubmitButton > button {
    background-color: #1677B8;
    color: white;
    border-radius: 9px;
    border: none;
    font-weight: 600;
    min-height: 42px;
}

div.stButton > button:hover,
div.stFormSubmitButton > button:hover {
    background-color: #105D91;
    color: white;
}

hr {
    border-color: #E2E8F0;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD COMPLAINTS
# --------------------------------------------------

def load_complaints():

    if not COMPLAINTS_FILE.exists():
        return []

    with open(
        COMPLAINTS_FILE,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)
        return list(reader)


# --------------------------------------------------
# UPDATE COMPLAINT STATUS
# --------------------------------------------------

def update_complaint_status(complaint_id, new_status):

    complaints = load_complaints()

    for complaint in complaints:

        if complaint["complaint_id"] == complaint_id:
            complaint["status"] = new_status

    if not complaints:
        return False

    fieldnames = list(complaints[0].keys())

    with open(
        COMPLAINTS_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(complaints)

    return True


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

header_col1, header_col2 = st.columns([4, 1])

with header_col1:

    st.markdown(
        '<div class="main-header">🎓 Admin Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-header">'
        'Smart Complaint Management System | Tanta University'
        '</div>',
        unsafe_allow_html=True
    )

with header_col2:

    st.markdown(
        "<div style='text-align:right; color:#1677B8; "
        "font-weight:700; padding-top:15px;'>"
        "ADMIN PANEL"
        "</div>",
        unsafe_allow_html=True
    )

st.divider()


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

complaints = load_complaints()

total_complaints = len(complaints)

pending = sum(
    1 for c in complaints
    if c.get("status") == "Pending"
)

under_review = sum(
    1 for c in complaints
    if c.get("status") == "Under Review"
)

in_progress = sum(
    1 for c in complaints
    if c.get("status") == "In Progress"
)

resolved = sum(
    1 for c in complaints
    if c.get("status") == "Resolved"
)

rejected = sum(
    1 for c in complaints
    if c.get("status") == "Rejected"
)

active_complaints = pending + under_review + in_progress


# --------------------------------------------------
# STATISTICS CARDS
# --------------------------------------------------

st.markdown(
    '<div class="section-title">📊 Complaints Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Complaints",
        total_complaints,
        help="All submitted complaints"
    )

with col2:
    st.metric(
        "Pending",
        pending,
        delta="Needs attention",
        delta_color="inverse"
    )

with col3:
    st.metric(
        "In Progress",
        under_review + in_progress,
        delta="Under processing",
        delta_color="off"
    )

with col4:
    st.metric(
        "Resolved",
        resolved,
        delta="Completed",
        delta_color="normal"
    )


# --------------------------------------------------
# STATUS DISTRIBUTION
# --------------------------------------------------

st.markdown(
    '<div class="section-title">📈 Complaint Status Distribution</div>',
    unsafe_allow_html=True
)

if total_complaints > 0:

    status_data = [
        ("Pending", pending, "#DC4545"),
        ("Under Review", under_review, "#E9A23B"),
        ("In Progress", in_progress, "#2689C7"),
        ("Resolved", resolved, "#239B70"),
        ("Rejected", rejected, "#64748B")
    ]

    for status_name, count, color in status_data:

        percentage = (count / total_complaints) * 100

        label_col, bar_col, percent_col = st.columns([1.3, 4, 0.6])

        with label_col:
            st.write(status_name)

        with bar_col:
            st.progress(
                percentage / 100,
                text=f"{count} complaints"
            )

        with percent_col:
            st.write(f"{percentage:.0f}%")

else:

    st.info("No complaint statistics available yet.")

st.divider()


# --------------------------------------------------
# SEARCH AND FILTERS
# --------------------------------------------------

st.markdown(
    '<div class="section-title">📋 Manage Complaints</div>',
    unsafe_allow_html=True
)

filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])

with filter_col1:

    search_id = st.text_input(
        "🔍 Search by Complaint ID",
        placeholder="Example: TC-2026-ABC123"
    )

with filter_col2:

    selected_filter = st.selectbox(
        "Filter by Status",
        [
            "All",
            "Pending",
            "Under Review",
            "In Progress",
            "Resolved",
            "Rejected"
        ]
    )

with filter_col3:

    categories = ["All"] + sorted(set(
        c.get("complaint_type", "")
        for c in complaints
        if c.get("complaint_type")
    ))

    selected_category = st.selectbox(
        "Filter by Category",
        categories
    )


filtered_complaints = complaints

if search_id:

    filtered_complaints = [
        c for c in filtered_complaints
        if search_id.lower() in c.get("complaint_id", "").lower()
    ]

if selected_filter != "All":

    filtered_complaints = [
        c for c in filtered_complaints
        if c.get("status") == selected_filter
    ]

if selected_category != "All":

    filtered_complaints = [
        c for c in filtered_complaints
        if c.get("complaint_type") == selected_category
    ]


# --------------------------------------------------
# COMPLAINTS TABLE
# --------------------------------------------------

if filtered_complaints:

    table_data = []

    for c in filtered_complaints:

        table_data.append({
            "Complaint ID": c.get("complaint_id", ""),
            "Student": c.get("student_name", ""),
            "Student ID": c.get("student_id", ""),
            "AI Category": c.get("ai_category", ""),
            "Priority": c.get("priority", ""),
            "College": c.get("college", ""),
            "Category": c.get("complaint_type", ""),
            "Title": c.get("title", ""),
            "Status": c.get("status", ""),
            "Date": c.get("created_at", "")
        })

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"Showing {len(filtered_complaints)} complaint(s)"
    )

else:

    st.info("No complaints match your search or filters.")


st.divider()


# --------------------------------------------------
# COMPLAINT DETAILS
# --------------------------------------------------

st.markdown(
    '<div class="section-title">🔎 Complaint Details</div>',
    unsafe_allow_html=True
)

if filtered_complaints:

    complaint_ids = [
        c["complaint_id"]
        for c in filtered_complaints
    ]

    selected_id = st.selectbox(
        "Select a complaint to view its details",
        complaint_ids
    )

    selected_complaint = next(
        c for c in filtered_complaints
        if c["complaint_id"] == selected_id
    )

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:

        st.markdown("#### 🏛️ Student's College")

        st.write(
            selected_complaint.get("college", "Not available")
        )

        st.markdown("#### 📝 Complaint Title")

        st.write(
            selected_complaint.get("title", "Not available")
        )

        st.markdown("#### 📂 Complaint Category")

        st.write(
            selected_complaint.get("complaint_type", "Not available")
        )

    with detail_col2:

        st.markdown("#### 🆔 Complaint ID")

        st.code(selected_id)

        st.markdown("#### 📌 Current Status")

        current_status = selected_complaint.get("status", "Pending")

        status_colors = {
            "Pending": "#DC4545",
            "Under Review": "#E9A23B",
            "In Progress": "#2689C7",
            "Resolved": "#239B70",
            "Rejected": "#64748B"
        }

        status_color = status_colors.get(
            current_status,
            "#64748B"
        )

        st.markdown(
            f"""
            <div style="
                background-color:{status_color}20;
                color:{status_color};
                padding:10px 15px;
                border-radius:9px;
                font-weight:700;
                display:inline-block;
            ">
                {current_status}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("#### 📅 Submission Date")

        st.write(
            selected_complaint.get("created_at", "Not available")
        )

    st.markdown("#### 📄 Complaint Description")

    st.info(
        selected_complaint.get("details", "No details available")
    )

    st.divider()


    # --------------------------------------------------
    # UPDATE COMPLAINT
    # --------------------------------------------------

    st.markdown(
        '<div class="section-title">✏️ Update Complaint</div>',
        unsafe_allow_html=True
    )

    statuses = [
        "Pending",
        "Under Review",
        "In Progress",
        "Resolved",
        "Rejected"
    ]

    with st.form("update_complaint_form"):

        new_status = st.selectbox(
            "Select New Status",
            statuses,
            index=statuses.index(current_status)
            if current_status in statuses else 0
        )

        admin_note = st.text_area(
            "Message for Student",
            placeholder="Write a message to inform the student about the complaint update..."
        )

        submitted = st.form_submit_button(
            "💾 Save Complaint Update",
            use_container_width=True
        )

        if submitted:

            if new_status == current_status and not admin_note.strip():

                st.warning(
                    "Please change the status or write an update message."
                )

            else:

                try:

                    update_complaint_status(
                        selected_id,
                        new_status
                    )

                    add_complaint_update(
                        selected_id,
                        new_status,
                        admin_note.strip()
                    )

                    st.success(
                        "Complaint updated successfully!"
                    )

                    st.rerun()

                except PermissionError:

                    st.error(
                        "Cannot update the complaint file. "
                        "Please close it in WPS Office or another program and try again."
                    )

else:

    st.info(
        "Submit a complaint first to view and manage its details."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        color:#94A3B8;
        font-size:13px;
        padding:10px;
    ">
        Smart Complaint Management System | Tanta University
    </div>
    """,
    unsafe_allow_html=True
) 
