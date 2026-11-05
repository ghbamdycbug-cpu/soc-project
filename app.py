
from flask import Flask, request
import os, re
from urllib.parse import urlparse

app = Flask(__name__)

def check_link(url):
    score = 0
    reasons = []
    url_low = url.lower()
    parsed = urlparse(url if "://" in url else "http://" + url)

    # 1. IP بدل اسم نطاق
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', parsed.netloc.split(':')[0]):
        score += 40
        reasons.append("⚠️ يستخدم عنوان IP بدل اسم نطاق - علامة تصيد قوية")
    # 2. روابط مختصرة
    if any(x in url_low for x in ['bit.ly','tinyurl','t.co','goo.gl','is.gd','cutt.ly']):
        score += 30
        reasons.append("⚠️ رابط مختصر يخفي الوجهة الحقيقية")
    # 3. كلمات مشبوهة
    for w in ['login','verify','secure','account','bank','free','win','prize','update','confirm']:
        if w in url_low:
            score += 10
            reasons.append(f"⚠️ يحتوي على كلمة مشبوهة: {w}")
    # 4. @ في الرابط
    if '@' in url:
        score += 25
        reasons.append("⚠️ يحتوي على @ لتضليل المستخدم")
    # 5. https ؟
    if not url_low.startswith('https://'):
        score += 15
        reasons.append("⚠️ لا يستخدم HTTPS آمن")
    # 6. طول مشبوه
    if len(url) > 75:
        score += 10
        reasons.append("⚠️ رابط طويل بشكل مشبوه")

    if score >= 50:
        return "🔴 خطير - تصيد محتمل!", "red", score, reasons
    elif score >= 25:
        return "🟡 مشبوه - انتبه!", "orange", score, reasons
    else:
        return "🟢 آمن على الأغلب", "green", score, reasons

@app.route('/', methods=['GET','POST'])
def home():
    result_html = ""
    logs = ""
    try:
        if os.path.exists("access.log"):
            with open("access.log") as f:
                logs = "<br>".join(f.read().splitlines()[-20:])
    except:
        pass

    if request.method == 'POST':
        url = request.form.get('url','').strip()
        if url:
            verdict, color, score, reasons = check_link(url)
            reasons_html = "<br>".join(reasons) if reasons else "✅ لا توجد علامات مشبوهة واضحة"
            result_html = f"""
            <div style="background:#1e293b;padding:15px;border-radius:10px;border:2px solid {color};margin-top:15px">
                <h3 style="color:{color}">{verdict} - درجة الخطر: {score}/100</h3>
                <p><b>الرابط:</b> {url}</p>
                <p>{reasons_html}</p>
            </div>
            """

    files = "<br>".join(os.listdir("."))

    return f"""
    <html dir="rtl" style="font-family:sans-serif;background:#0f172a;color:white">
    <div style="max-width:700px;margin:auto;padding:20px">
    <h1>🛡️ SOC - مركز العمليات الأمنية</h1>
    <p>أهلا بك يا مريم - نظامك شغال لايف</p>

    <div style="background:#1e293b;padding:15px;border-radius:10px">
    <h2>🔗 فاحص الروابط - كاشف التصيد</h2>
    <form method="POST">
    <input name="url" placeholder="الصق الرابط هنا ... https://example.com" style="width:75%;padding:12px;border-radius:8px;border:none">
    <button style="padding:12px 20px;background:#dc2626;color:white;border:none;border-radius:8px;font-weight:bold">افحص</button>
    </form>
    {result_html}
    </div>

    <h2>📋 آخر تسجيل - access.log</h2>
    <div style="background:black;padding:15px;border-radius:10px;direction:ltr;text-align:left">{logs}</div>
    <h2>🛠️ ملفاتك</h2>
    <p>{files}</p>
    </div>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
