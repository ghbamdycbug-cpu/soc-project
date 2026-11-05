

from flask import Flask, request
from urllib.parse import urlparse
import re

app = Flask(__name__)

def check_link(URL):
    النتيجة = 0
    اسباب = []
    url_low = URL.lower()
    تحليله = urlparse(URL if "://" in URL else "http://" + URL)
    دومين = تحليله.netloc.lower().replace("www.", "")

    # 1. IP بدل اسم النطاق
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', دومين):
        النتيجة += 40
        اسباب.append("⚠️ علامة تصيد قوية - IP بدل اسم نطاق")

    # 2. روابط مختصرة
    if any(x in url_low for x in ['bit.ly','tinyurl','t.co','is.gd']):
        النتيجة += 30
        اسباب.append("⚠️ رابط مختصر يخفي الوجهة الحقيقية")

    # 3. انتحال علامة - هذا الجديد والقوي!
    brands = ['google','facebook','instagram','paypal','amazon','apple','microsoft','bank','whatsapp']
    for b in brands:
        if b in url_low and not دومين.endswith(b + ".com") and دومين != b + ".com":
            # تأكد انه مو الدومين الأصلي
            if b in دومين and دومين != b + ".com":
                النتيجة += 40
                اسباب.append(f"⚠️ انتحال علامة تجارية: يحاول تقليد {b} وهو مو موقعه الأصلي")
                break

    # 4. نطاقات رخيصة يستخدمها الهاكرز
    if دومين.endswith(('.xyz','.top','.shop','.click','.online','.site','.buzz','.live')):
        النتيجة += 20
        اسباب.append("⚠️ نطاق رخيص مشبوه يكثر استخدامه في التصيد")

    # 5. شرطات كثيرة
    if دومين.count('-') >= 2:
        النتيجة += 15
        اسباب.append("⚠️ فيه شرطات كثيرة - أسلوب تصيد شائع")

    # 6. كلمات مشبوهة
    كلمات = ['login','secure','verify','account','bank','password','signin','update','confirm']
    for w in كلمات:
        if w in url_low:
            النتيجة += 10
            اسباب.append(f"⚠️ يحتوي على كلمة مشبوهة: {w}")

    # 7. علامة @ في الرابط
    if '@' in URL:
        النتيجة += 25
        اسباب.append("⚠️ فيه @ في الرابط")

    if النتيجة > 100:
        النتيجة = 100

    return النتيجة, اسباب

@app.route('/', methods=['GET','POST'])
def home():
    نتيجة = None
    اسباب = []
    رابط = ""
    if request.method == 'POST':
        رابط = request.form.get('url','')
        if رابط:
            نتيجة, اسباب = check_link(رابط)
    return f"""
    <div style="direction:rtl; text-align:center; font-family:Arial; background:#0a1929; color:white; min-height:100vh; padding:20px;">
    <h2>🛡️ فاحص الروابط - كاشف التصيد</h2>
    <form method="POST">
    <input name="url" value="{رابط}" placeholder="الصق الرابط هنا https://example.com" style="width:90%; padding:12px; border-radius:10px; border:none; text-align:center;">
    <br><br>
    <button style="background:#ff3b3b; color:white; padding:12px 30px; border:none; border-radius:10px; font-size:18px;">افحص</button>
    </form>
    <br>
    {'<h2 style="color:' + ('#00ff88' if نتيجة < 30 else '#ffcc00' if نتيجة < 60 else '#ff3b3b') + f';">درجة الخطر: {نتيجة}/100</h2>' + '<br>'.join([f'<p>{s}</p>' for s in اسباب]) if نتيجة is not None else ''}
    </div>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
