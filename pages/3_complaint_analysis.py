import streamlit as st
import csv
import re
from pathlib import Path
from datetime import datetime

# ==========================================
# 1. PAGE SETTINGS
# ==========================================

st.set_page_config(
    page_title="AI Complaint Analysis",
    page_icon="🤖",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent
COMPLAINTS_FILE = BASE_DIR / "complaints.csv"


# ==========================================
# 2. DESIGN
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #F3F6FC;
}

.main-header {
    background: linear-gradient(110deg, #2457A6, #548BE5);
    padding: 30px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}

.main-header h1 {
    color: white;
    font-size: 30px;
    margin-bottom: 8px;
}

.main-header p {
    color: #EAF2FF;
    margin: 0;
}

.metric-card {
    background: white;
    border: 1px solid #E3EAF5;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}

.metric-number {
    color: #2457A6;
    font-size: 30px;
    font-weight: bold;
}

.metric-label {
    color: #718096;
    font-size: 14px;
}

.result-card {
    background: white;
    border: 1px solid #E3EAF5;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 15px;
}

.stButton > button {
    background-color: #2457A6;
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: bold;
    min-height: 45px;
}

.stButton > button:hover {
    background-color: #19447F;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. LOAD COMPLAINTS
# ==========================================

def load_complaints():

    if not COMPLAINTS_FILE.exists():
        return []

    with open(
        COMPLAINTS_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)
        return list(reader)


# ==========================================
# 4. TEXT PROCESSING
# ==========================================

def normalize_text(text):

    text = str(text).lower().strip()

    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ة", "ه", text)

    return text


# ==========================================
# 5. COMPLAINT CLASSIFICATION
# ==========================================

CATEGORY_RULES = {

    "Technical Issues": [
        "internet", "wifi", "network", "computer",
        "system", "website", "password", "login",
        "technical", "server", "software",
        "انترنت", "واي فاي", "شبكه", "شبكة",
        "كمبيوتر", "حاسب", "موقع", "سيستم",
        "كلمه المرور", "تسجيل الدخول", "تقني"
    ],

    "Academic Affairs": [
        "exam", "examination", "grade", "result",
        "lecture", "professor", "course", "schedule",
        "marks", "registration", "academic",
        "امتحان", "اختبار", "درجات", "نتيجه",
        "نتيجة", "محاضره", "محاضرة", "دكتور",
        "ماده", "مادة", "جدول", "تسجيل", "اكاديمي"
    ],

    "Student Affairs": [
        "student card", "student affairs",
        "certificate", "documents", "admission",
        "scholarship", "student service",
        "بطاقه", "بطاقة", "شئون الطلاب",
        "شؤون الطلاب", "شهاده", "شهادة",
        "اوراق", "أوراق", "قبول", "منحه", "منحة"
    ],

    "Facilities and Maintenance": [
        "classroom", "building", "chair",
        "air conditioning", "electricity",
        "water", "cleaning", "laboratory",
        "room", "maintenance",
        "قاعه", "قاعة", "مبني", "مبنى",
        "كرسي", "تكييف", "كهرباء", "مياه",
        "نظافه", "نظافة", "معمل", "صيانه", "صيانة"
    ],

    "Financial Affairs": [
        "payment", "fees", "money", "refund",
        "financial", "tuition", "payment problem",
        "مصروفات", "رسوم", "فلوس",
        "دفع", "استرداد", "مالي", "مصاريف"
    ]
}


DEPARTMENT_RULES = {
    "Technical Issues": "IT Support Department",
    "Academic Affairs": "Academic Affairs Department",
    "Student Affairs": "Student Affairs Department",
    "Facilities and Maintenance": "Facilities and Maintenance Department",
    "Financial Affairs": "Financial Affairs Department",
    "General Complaint": "University Administration"
}


def classify_complaint(text):

    normalized = normalize_text(text)

    scores = {}

    for category, keywords in CATEGORY_RULES.items():

        score = 0

        for keyword in keywords:

            if normalize_text(keyword) in normalized:
                score += 1

        scores[category] = score

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "General Complaint"

    return best_category


# ==========================================
# 6. PRIORITY DETECTION
# ==========================================

HIGH_PRIORITY_WORDS = [
    "urgent", "emergency", "danger", "unsafe",
    "serious", "immediately", "critical",
    "unable to attend", "all students",
    "خطر", "طارئ", "عاجل", "فورا",
    "فوراً", "خطير", "خطيره", "غير امن",
    "غير آمن", "كل الطلاب", "تعطيل كامل"
]

MEDIUM_PRIORITY_WORDS = [
    "delay", "problem", "issue", "repeated",
    "affecting", "not working", "cannot",
    "تاخير", "تأخير", "مشكله", "مشكلة",
    "متكرر", "تاثير", "تأثير", "لا يعمل",
    "مش شغال", "مش شغاله", "غير متاح"
]


def detect_priority(text):

    normalized = normalize_text(text)

    high_matches = [
        word for word in HIGH_PRIORITY_WORDS
        if normalize_text(word) in normalized
    ]

    medium_matches = [
        word for word in MEDIUM_PRIORITY_WORDS
        if normalize_text(word) in normalized
    ]

    if high_matches:
        return "High", "The complaint contains urgent or serious indicators."

    if medium_matches:
        return "Medium", "The complaint contains indicators of an issue requiring attention."

    if len(normalized.split()) > 40:
        return "Medium", "The complaint is relatively detailed and needs review."

    return "Low", "No clear urgent or serious indicators were detected."


# ==========================================
# 7. SENTIMENT ANALYSIS
# ==========================================

SENTIMENT_WORDS = {

    "Angry": [
        "angry", "furious", "unacceptable",
        "terrible", "hate", "غاضب", "غضب",
        "سيء جدا", "مش مقبول", "كارثي"
    ],

    "Frustrated": [
        "frustrated", "disappointed", "annoyed",
        "tired", "upset", "محبط", "احباط",
        "متضايق", "زهقان", "تعبت", "مستاء"
    ],

    "Worried": [
        "worried", "afraid", "concerned",
        "anxious", "قلقان", "قلق",
        "خايف", "خائف", "خوف"
    ],

    "Positive": [
        "thank you", "satisfied", "appreciate",
        "شكرا", "راضي", "ممتن", "مبسوط"
    ]
}


def analyze_sentiment(text):

    normalized = normalize_text(text)

    scores = {}

    for sentiment, keywords in SENTIMENT_WORDS.items():

        scores[sentiment] = sum(
            1 for word in keywords
            if normalize_text(word) in normalized
        )

    best_sentiment = max(scores, key=scores.get)

    if scores[best_sentiment] == 0:
        return "Neutral"

    return best_sentiment


# ==========================================
# 8. KEYWORD EXTRACTION
# ==========================================

STOP_WORDS = {
    "the", "is", "are", "was", "were", "and",
    "or", "to", "of", "in", "on", "for",
    "with", "this", "that", "it", "my",
    "i", "we", "our", "a", "an", "have",
    "has", "been", "be", "not", "but",
    "في", "من", "على", "الي", "الى",
    "عن", "ان", "انا", "هو", "هي",
    "ده", "دي", "دا", "كان", "كانت",
    "مع", "و", "او", "اللي", "هذا",
    "هذه", "تم", "بعد", "قبل"
}


def extract_keywords(text):

    normalized = normalize_text(text)

    words = re.findall(r"\b[\w]+\b", normalized)

    result = []

    for word in words:

        if len(word) < 3:
            continue

        if word in STOP_WORDS:
            continue

        if word not in result:
            result.append(word)

    return result[:8]


# ==========================================
# 9. COMPLAINT SUMMARY
# ==========================================

def summarize_complaint(text):

    text = str(text).strip()

    if not text:
        return "No complaint details available."

    sentences = re.split(r"(?<=[.!?؟])\s+", text)

    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    if not sentences:
        return text[:250]

    summary = " ".join(sentences[:2])

    if len(summary) > 300:
        summary = summary[:297] + "..."

    return summary


# ==========================================
# 10. DEPARTMENT RECOMMENDATION
# ==========================================

def recommend_department(category):

    return DEPARTMENT_RULES.get(
        category,
        "University Administration"
    )


# ==========================================
# 11. SOLUTION RECOMMENDATION
# ==========================================

SOLUTIONS = {

    "Technical Issues":
        "Refer the complaint to IT Support to investigate the technical problem and restore the affected service.",

    "Academic Affairs":
        "Refer the complaint to Academic Affairs to review the academic issue and coordinate with the responsible faculty member.",

    "Student Affairs":
        "Refer the complaint to Student Affairs to review the student's request and provide the required service.",

    "Facilities and Maintenance":
        "Assign the issue to the maintenance team to inspect the facility and arrange the necessary repair.",

    "Financial Affairs":
        "Refer the complaint to Financial Affairs to review the payment or fees issue and verify the relevant records.",

    "General Complaint":
        "Send the complaint to University Administration for review and determine the appropriate department."
}


def recommend_solution(category, priority):

    solution = SOLUTIONS.get(
        category,
        SOLUTIONS["General Complaint"]
    )

    if priority == "High":
        solution += " This complaint should be reviewed urgently."

    elif priority == "Medium":
        solution += " Follow up to ensure the issue is resolved in a reasonable time."

    return solution


# ==========================================
# 12. COMPLETE ANALYSIS
# ==========================================

def analyze_complaint(complaint):

    title = complaint.get("title", "")
    details = complaint.get("details", "")

    full_text = title + " " + details

    category = classify_complaint(full_text)

    priority, priority_reason = detect_priority(full_text)

    sentiment = analyze_sentiment(full_text)

    keywords = extract_keywords(full_text)

    summary = summarize_complaint(details)

    department = recommend_department(category)

    recommendation = recommend_solution(
        category,
        priority
    )

    return {
        "category": category,
        "priority": priority,
        "priority_reason": priority_reason,
        "sentiment": sentiment,
        "keywords": keywords,
        "summary": summary,
        "department": department,
        "recommendation": recommendation
    }


# ==========================================
# 13. SAVE ANALYSIS
# ==========================================

def save_analysis(complaint_id, result):

    rows = load_complaints()

    if not rows:
        raise ValueError("No complaints were found.")

    new_fields = [
        "ai_category",
        "priority",
        "reasoning",
        "ai_sentiment",
        "ai_keywords",
        "ai_summary",
        "ai_department",
        "ai_recommendation",
        "ai_analyzed_at"
    ]

    fieldnames = list(rows[0].keys())

    for field in new_fields:
        if field not in fieldnames:
            fieldnames.append(field)

    found = False

    for row in rows:

        if row.get("complaint_id") == complaint_id:

            row["ai_category"] = result["category"]
            row["priority"] = result["priority"]
            row["reasoning"] = result["priority_reason"]
            row["ai_sentiment"] = result["sentiment"]

            row["ai_keywords"] = ", ".join(
                result["keywords"]
            )

            row["ai_summary"] = result["summary"]
            row["ai_department"] = result["department"]
            row["ai_recommendation"] = result["recommendation"]

            row["ai_analyzed_at"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            found = True
            break

    if not found:
        raise ValueError("Complaint ID was not found.")

    with open(
        COMPLAINTS_FILE,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore"
        )

        writer.writeheader()
        writer.writerows(rows)


# ==========================================
# 14. PAGE HEADER
# ==========================================

st.markdown("""
<div class="main-header">
    <h1>🤖 AI Complaint Analysis</h1>
    <p>Smart complaint classification, priority detection and recommendations</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 15. LOAD DATA
# ==========================================

complaints = load_complaints()

if not complaints:

    st.warning("No complaints found. Please submit a complaint first.")
    st.stop()


analyzed_count = sum(
    1 for row in complaints
    if (row.get("ai_analyzed_at") or "").strip()
)

waiting_count = len(complaints) - analyzed_count


# ==========================================
# 16. STATISTICS
# ==========================================

st.markdown("### Analysis Overview")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-number">{len(complaints)}</div>
        <div class="metric-label">Total Complaints</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-number">{analyzed_count}</div>
        <div class="metric-label">Analyzed Complaints</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-number">{waiting_count}</div>
        <div class="metric-label">Waiting for Analysis</div>
    </div>
    """, unsafe_allow_html=True)


st.write("")


# ==========================================
# 17. SELECT COMPLAINT
# ==========================================

st.markdown("### Select Complaint")

options = {}

for row in complaints:

    complaint_id = row.get("complaint_id", "")

    if complaint_id:

        title = row.get("title", "Untitled")

        options[complaint_id] = (
            f"{complaint_id} - {title}"
        )

if not options:
    st.warning("No valid Complaint IDs were found.")
    st.stop()


selected_id = st.selectbox(
    "Choose a complaint to analyze",
    list(options.keys()),
    format_func=lambda x: options[x]
)

selected_complaint = next(
    row for row in complaints
    if row.get("complaint_id") == selected_id
)


# ==========================================
# 18. COMPLAINT DETAILS
# ==========================================

st.markdown("### Complaint Information")

with st.container(border=True):

    left, right = st.columns(2)

    with left:

        st.write("**Complaint ID**")
        st.write(selected_complaint.get("complaint_id", "N/A"))

        st.write("**College**")
        st.write(selected_complaint.get("college", "N/A"))

        st.write("**Complaint Type**")
        st.write(selected_complaint.get("complaint_type", "N/A"))

    with right:

        st.write("**Title**")
        st.write(selected_complaint.get("title", "N/A"))

        st.write("**Current Status**")
        st.write(selected_complaint.get("status", "N/A"))

        st.write("**Submission Date**")
        st.write(selected_complaint.get("created_at", "N/A"))

    st.divider()

    st.write("**Complaint Details**")

    st.write(
        selected_complaint.get(
            "details",
            "No details available."
        )
    )


# ==========================================
# 19. RUN ANALYSIS
# ==========================================

st.write("")

if st.button(
    "🤖 Analyze Complaint",
    use_container_width=True
):

    if not selected_complaint.get("details", "").strip():

        st.error("This complaint has no details to analyze.")

    else:

        try:

            with st.spinner("Analyzing complaint..."):

                result = analyze_complaint(
                    selected_complaint
                )

                save_analysis(
                    selected_id,
                    result
                )

                st.session_state["analysis_result"] = result
                st.session_state["analysis_id"] = selected_id

            st.success("Complaint analysis completed successfully!")

        except PermissionError:

            st.error(
                "Cannot save the analysis. "
                "Please close complaints.csv in WPS or Excel and try again."
            )

        except Exception as error:

            st.error(f"An error occurred: {error}")


# ==========================================
# 20. DISPLAY RESULTS
# ==========================================

result = None

if (
    st.session_state.get("analysis_id") == selected_id
    and "analysis_result" in st.session_state
):

    result = st.session_state["analysis_result"]

else:

    if selected_complaint.get("ai_analyzed_at", "").strip():

        result = {
            "category": selected_complaint.get("ai_category", "N/A"),
            "priority": selected_complaint.get("priority", "N/A"),
            "priority_reason": selected_complaint.get("reasoning", ""),
            "sentiment": selected_complaint.get("ai_sentiment", "N/A"),
            "keywords": [
                word.strip()
                for word in selected_complaint.get("ai_keywords", "").split(",")
                if word.strip()
            ],
            "summary": selected_complaint.get("ai_summary", "N/A"),
            "department": selected_complaint.get("ai_department", "N/A"),
            "recommendation": selected_complaint.get("ai_recommendation", "N/A")
        }


if result:

    st.markdown("---")
    st.markdown("## 📊 Analysis Results")

    # Category and priority
    col1, col2 = st.columns(2)

    with col1:

        st.markdown("#### Complaint Classification")

        st.info(result["category"])

    with col2:

        st.markdown("#### Priority Level")

        if result["priority"] == "High":
            st.error("🔴 HIGH PRIORITY")

        elif result["priority"] == "Medium":
            st.warning("🟠 MEDIUM PRIORITY")

        else:
            st.success("🟢 LOW PRIORITY")


    # Sentiment and department
    col3, col4 = st.columns(2)

    with col3:

        st.markdown("#### Sentiment Analysis")

        st.info(result["sentiment"])

    with col4:

        st.markdown("#### Responsible Department")

        st.info(result["department"])


    # Summary
    st.markdown("### 📝 Complaint Summary")

    with st.container(border=True):
        st.write(result["summary"])


    # Keywords
    st.markdown("### 🔑 Extracted Keywords")

    if result["keywords"]:

        st.write("  •  ".join(result["keywords"]))

    else:

        st.write("No important keywords were detected.")


    # Reasoning
    st.markdown("### 🧠 Priority Reasoning")

    with st.container(border=True):
        st.write(result["priority_reason"])


    # Recommendation
    st.markdown("### 💡 Recommended Solution")

    with st.container(border=True):
        st.write(result["recommendation"])


    st.caption(
        "This is a rule-based analysis prototype. "
        "Results are suggestions and should be reviewed by the administrator."
    )

else:

    st.info(
        "Select a complaint and click Analyze Complaint "
        "to view its analysis results."
    )  
