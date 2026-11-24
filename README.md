# tanta-complaints-classifier-preview

نظام شكاوى جامعة طنطا — نسخة تجريبية (Streamlit + تصنيف تلقائي للشكاوى بالذكاء الاصطناعي)

رابط التجربة المباشر: https://tanta-complaints-classifier-preview-dwjve3zou4rk53pcdiputx.streamlit.app/

## التشغيل على جهازك (VS Code)

1. ثبّت Python 3.10 أو أحدث.
2. نزّل المشروع: `git clone https://github.com/medo66reda66/tanta-complaints-classifier-preview.git` أو من زر Code اختر Download ZIP.
3. افتح فولدر المشروع في VS Code وافتح Terminal.
4. ثبّت المكتبات: `pip install -r requirements.txt`
5. شغّل الموقع: `streamlit run app.py`
6. هيفتح المتصفح تلقائيا على http://localhost:8501

## ملاحظات

- صفحات الأدمن (Admin Dashboard و Complaint Analysis) محمية بكلمة سر.
- الشكاوى بتتخزن في ملفات CSV محلية، ودي نسخة تجريبية للعرض فقط وليست لاستقبال شكاوى حقيقية.
- بيانات التدريب في complaints_training.csv وهي شكاوى تجريبية مجهولة المصدر.
