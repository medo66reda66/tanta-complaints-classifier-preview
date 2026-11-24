from typing import Dict, List, Tuple
from ai_agent import ComplaintAIAgent


class ComplaintService:
    def __init__(self, model_path: str = "complaint_agent.joblib"):
        self.agent = ComplaintAIAgent(model_path=model_path)
        self._ensure_ready()

    def _ensure_ready(self):
        if not self.agent.load():
            texts, labels = self.agent.load_from_excel()
            self.agent.train(texts, labels)

    def get_categories(self) -> List[str]:
        return sorted(set(self.agent.labels))

    def classify(self, text: str) -> Tuple[str, float]:
        return self.agent.predict(text)

    def learn_feedback(self, text: str, correct_category: str):
        self.agent.learn(text, correct_category)

    # دالة احتياطية مؤقتة لحين جاهزية جزء الـ Reasoning من الفريق
    def estimate_priority_fallback(self, text: str, category: str, confidence: float) -> Dict[str, str]:
        urgent_keywords = ["امتحان", "نتيجة", "كارنيه", "حريق", "كهرباء", "مياه", "خطر", "عاجل", "معمل"]
        clean_input = (text or "").strip()

        if any(word in clean_input for word in urgent_keywords):
            return {
                "priority": "High",
                "reason": "تحتوي الشكوى على كلمات مرتبطة بمتطلبات عاجلة أو تشغيلية مؤثرة.",
            }
        if confidence < 25.0:
            return {
                "priority": "Medium",
                "reason": "نسبة ثقة التصنيف متوسطة/منخفضة وتحتاج مراجعة لتحديد الأهمية بدقة.",
            }
        return {
            "priority": "Low",
            "reason": f"تصنيف مبدئي ({category}) بدون مؤشرات استعجال فورية.",
        }
