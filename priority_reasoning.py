import re

# ---------- 1) Knowledge base ----------

DEFAULT_BASE = 15

CATEGORY_BASE = {
    # سلامة وصحة ودعم
    "Campus Safety & Security": 35, "Medical Services": 35, "Psychological Support": 35,
    "Accessibility": 30, "Facilities & Accessibility": 30, "Fair Treatment": 30,
    # فلوس وحقوق مباشرة للطالب
    "Duplicate Payment": 28, "Payment Verification": 28, "Financial Affairs": 22,
    "Administrative & Financial Services": 22, "Installment Plans": 15,
    # امتحانات وسجلات أكاديمية
    "Exams & Results": 28, "Exams & Assessment": 28, "Exam Scheduling": 28,
    "Academic Records": 25, "Graduation Documents": 25, "Re-enrollment": 25,
    "Student Registration": 25, "Department Assignment": 25, "Academic Requests": 22,
    "Attendance Management": 18,
    # دراسة وخدمات إدارية
    "Academic Affairs": 18, "Academic & Student Affairs": 18, "Student Administrative Services": 18,
    "General Student Services": 18, "Administrative Communication": 15,
    "Schedule Changes": 15, "Lecture Timing": 15,
    "Course Difficulty": 12, "Curriculum": 12, "Curriculum Coverage": 12, "Curriculum Updates": 10,
    "Student Participation": 10,
    # تقنية
    "Technical Issues": 15, "IT & E-Learning": 15,
    # مرافق وسكن
    "Campus Facilities": 18, "Facilities & Maintenance": 15, "Facilities & Equipment": 15,
    "University Housing": 18, "Student Housing & Food Services": 15, "Cleanliness & Sanitation": 12,
    "Transportation": 12,
    # مكتبة وأنشطة وخدمات عامة (أقل استعجالًا)
    "Library Services": 8, "Library Furniture": 5, "Library Navigation": 5,
    "Digital Library System": 8, "Borrowing Records": 10, "Outdated References": 5,
    "Campus Services": 10, "Student Services": 8, "Student Facilities & Activities": 8,
    "Career & Training Support": 8,
}

# قواعد الاستدلال: (السبب, الوزن, الكلمات).  الوزن بالسالب = بينزّل الأولوية.
RULES = [
    ("خطر مباشر على السلامة", 35, [
        "خطر", "حريق", "طفايات", "مخارج الطوارئ", "اسلاك كهرباء", "مكشوفه", "انزلاق",
        "اغماء", "اصابه", "اصابات", "اسعافات"]),
    ("حرمان الطالب من حق أو خدمة", 25, [
        "اتمنعت", "ممنوع", "يهدد", "تهدد", "رغم استيفايي", "رغم اني دافع", "رغم اني رجعته",
        "لم يتم تسجيل", "غير مسجل", "ترفض رغم", "بترفض", "مش هنقدر نراجع"]),
    ("خسارة مالية أو خطأ في بيانات الطالب", 20, [
        "اتخصم", "استرد", "المبلغ مرتين", "خطا في", "بيانات غلط", "غير صحيح", "اسمي متسجل"]),
    ("طلب معلّق أو تأخير من غير رد", 15, [
        "لم اتلق", "من غير ما نعرف", "بدون توضيح", "معلقه", "فتره طويله", "منذ فتره",
        "بتتاخر", "بيتاخر", "تاخر", "لم يتم الرد", "محدش بلغنا"]),
    ("ضيق وقت أو ميعاد قريب", 15, [
        "بسرعه", "فورا", "في نفس اليوم", "قبل الامتحان", "بفاصل زمني قليل", "اخر اليوم"]),
    ("ذوي الإعاقة أو حالات خاصة", 15, [
        "ذوي الاعاقه", "ذوي الاحتياجات", "الكراسي المتحركه", "كرسي متحرك", "المصاعد", "مرضي", "نفسي"]),
    ("تأثير على عدد كبير من الطلاب", 10, [
        "الطلاب", "الطلبه", "كل الطلاب", "معظم", "اغلب", "ازدحام", "طوابير", "اعداد الطلاب"]),
    ("مشكلة متكررة أو مستمرة", 10, [
        "كل مره", "دايما", "دائما", "كل يوم", "كل اسبوع", "اوقات كتير", "مش بتتحل", "لسه"]),
    ("إجراء غير واضح (محتاج توضيح فقط)", -5, [
        "مش واضح", "غير واضح", "مش عارف", "مش عارفه", "مش بنعرف"]),
    ("تحسين أو راحة (مش عاجل)", -8, [
        "نرجو", "اتمنى", "غير مريحه", "قديمه", "مرتفعه", "اسعار", "ياريت"]),
]

LEVELS = [  # (حد أدنى للسكور, المستوى)
    (75, "حرجة"),
    (50, "عالية"),
    (25, "متوسطة"),
    (0, "منخفضة"),
]


# ---------- 2) Text normalization ----------
_DIACRITICS = re.compile(r"[\u064B-\u0652\u0640]")

def normalize(text: str) -> str:
    text = _DIACRITICS.sub("", str(text))
    text = re.sub("[إأآ]", "ا", text)
    text = text.replace("ى", "ي").replace("ة", "ه")
    return text.lower()


# ---------- 3) Reasoning engine ----------
def prioritize(text: str, category: str = "", confidence: float = 1.0) -> dict:
    norm = normalize(text)
    base = CATEGORY_BASE.get(category, DEFAULT_BASE)
    score = base
    reasons = [f"التصنيف '{category or 'غير محدد'}' وزنه الأساسي {base}"]

    for reason, weight, words in RULES:
        hits = [w for w in words if normalize(w) in norm]
        if hits:
            score += weight
            sign = "+" if weight > 0 else ""
            reasons.append(f"{reason} ({sign}{weight}) ← وجدنا: {', '.join(hits[:3])}")

    if confidence < 0.5:   # تصنيف مش مؤكد → نقلل الأثر شوية
        score *= 0.9
        reasons.append("ثقة التصنيف منخفضة (×0.9)")

    score = max(0, min(100, round(score)))
    level = next(name for limit, name in LEVELS if score >= limit)
    return {"priority": level, "score": score, "reasons": reasons}


if __name__ == "__main__":
    tests = [
        ("فيه أسلاك كهرباء مكشوفة في بعض الأماكن وده خطر على سلامة الطلاب", "Campus Safety & Security"),
        ("اتخصم مني المبلغ مرتين لما حاولت أدفع المصاريف أونلاين، ومحتاج أسترد المبلغ الزيادة بسرعة.", "Duplicate Payment"),
        ("المقاعد الموجودة في المكتبة غير مريحة، وبعضها مكسور ويحتاج إلى إصلاح.", "Library Furniture"),
    ]
    for t, c in tests:
        print(t, "->", prioritize(t, c))
