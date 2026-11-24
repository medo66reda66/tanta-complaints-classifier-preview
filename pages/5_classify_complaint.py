import streamlit as st
from agent_service import ComplaintService

st.set_page_config(page_title="Complaint Classifier", page_icon="🗂️", layout="centered")
st.title("🗂️ Complaint Classifier")
st.caption("Trained on the complaints in Tanta_University_Complaints_Final_Styled.xlsx")


@st.cache_resource
def get_service():
    return ComplaintService()


service = get_service()
st.write(f"Model trained on {len(service.agent.texts)} complaints across {len(service.get_categories())} categories.")

text = st.text_area("Enter a new complaint", height=140, placeholder="مثال: النت فاصل في المعمل")
if st.button("Classify"):
    if not text.strip():
        st.warning("Please enter a complaint.")
    else:
        top = service.agent.predict_top(text, 3)
        st.success(f"Category: {top[0][0]}  (match score {top[0][1]}, relative, not a probability)")
        st.write("Other likely categories:")
        for cat, p in top[1:]:
            st.write(f"- {cat} (score {p})")
