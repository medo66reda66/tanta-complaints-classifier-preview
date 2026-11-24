import os
import re
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)
    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class ComplaintAIAgent:
    def __init__(self, model_path: str = "complaint_agent.joblib"):
        self.model_path = model_path
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(preprocessor=clean_text, analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True)),
            ("clf", LinearSVC(C=1.0)),
        ])
        self.texts: list[str] = []
        self.labels: list[str] = []
        self.is_trained: bool = False

    def load_from_excel(
        self,
        excel_path: str = "Tanta_University_Complaints_Final_Styled.xlsx",
        sheet_name=0,
    ) -> tuple[list[str], list[str]]:
        import os
        csv_path = "complaints_training.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
        else:
            df = pd.read_excel(excel_path, sheet_name=sheet_name, header=1)
        df = df.dropna(subset=["Complaint", "Category"])
        texts = df["Complaint"].astype(str).tolist()
        labels = df["Category"].astype(str).str.strip().tolist()
        return texts, labels

    def train(self, texts: list[str], labels: list[str]):
        if not texts or len(texts) != len(labels):
            raise ValueError("النصوص والتصنيفات يجب ألا تكون فارغة ويجب أن يكون عددهما متساوياً.")
        self.texts = list(texts)
        self.labels = list(labels)
        self.pipeline.fit(self.texts, self.labels)
        self.is_trained = True
        self.save()

    def predict_top(self, text: str, k: int = 3) -> list[tuple[str, float]]:
        """Top-k categories with softmax-normalised scores (percent)."""
        if not self.is_trained:
            raise RuntimeError("الموديل لم يتم تدريبه بعد.")
        scores = self.pipeline.decision_function([text])[0]
        classes = self.pipeline.classes_
        e = np.exp((scores - scores.max()) * 3)
        probs = e / e.sum()
        idx = np.argsort(-probs)[:k]
        return [(str(classes[i]), round(float(probs[i]) * 100, 2)) for i in idx]

    def predict(self, text: str) -> tuple[str, float]:
        return self.predict_top(text, 1)[0]

    def learn(self, text: str, correct_label: str):
        clean_input = (text or "").strip()
        if not clean_input or not correct_label:
            return
        self.texts.append(clean_input)
        self.labels.append(correct_label.strip())
        self.pipeline.fit(self.texts, self.labels)
        self.is_trained = True
        self.save()

    def save(self):
        joblib.dump({
            "pipeline": self.pipeline,
            "texts": self.texts,
            "labels": self.labels,
            "is_trained": self.is_trained,
        }, self.model_path)

    def load(self) -> bool:
        if not os.path.exists(self.model_path):
            return False
        data = joblib.load(self.model_path)
        self.pipeline = data["pipeline"]
        self.texts = data["texts"]
        self.labels = data["labels"]
        self.is_trained = data["is_trained"]
        return True


if __name__ == "__main__":
    agent = ComplaintAIAgent()
    texts, labels = agent.load_from_excel()
    agent.train(texts, labels)
    print(f"تم تدريب الموديل بنجاح على {len(texts)} شكوى و {len(set(labels))} تصنيف.")

    sample = "النت فاصل في المعمل ومش عارفين نفتح موقع الكلية"
    pred, conf = agent.predict(sample)
    print(f"تجربة تصنيف: '{sample}' -> التصنيف: {pred} (نسبة الثقة: {conf}%)")
