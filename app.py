

 from flask import Flask, request
from urllib.parse import urlparse
import re

app = Flask(__name__)

def check_link(URL):
    score = 0
    reasons = []
    url_low = URL.lower()
    parsed = urlparse(URL if "://" in URL else "http://" + URL)
    domain = parsed.netloc.lower().replace("www.", "")

    # 1. IP instead of domain
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', domain):
        score += 40
        reasons.append("IP instead of domain name - strong phishing sign")

    # 2. Short links
    if any(x in url_low for x in ['bit.ly','tinyurl','t.co','is.gd']):
        score += 30
        reasons.append("Short link hides real destination")

    # 3. Brand impersonation - NEW STRONG CHECK
    brands = ['google','facebook','instagram','paypal','amazon','apple','microsoft','whatsapp']
    for b in brands:
        if b in domain and domain != b + ".com":
            score += 40
            reasons.append(f"Brand impersonation: tries to fake {b} but domain is not {b}.com")
            break

    # 4. Cheap TLDs
    if domain.endswith(('.xyz','.top','.shop','.click','.online','.site','.buzz','.live')):
        score += 20
        reasons.append("Cheap suspicious TLD used a lot in phishing")

    # 5. Many dashes
    if domain.count('-') >= 2:
        score += 15
        reasons.append("Many dashes - common phishing trick")

    # 6. Suspicious words
    words = ['login','secure','verify','account','bank','password','signin','update','confirm']
    for w in words:
        if w in url_low:
            score += 10
            reasons.append(f"Contains suspicious word: {w}")

    # 7. @ in URL
    if '@' in URL:
        score += 25
        reasons.append("Contains @ in URL")

    if score > 100:
        score = 100
    return score, reasons

@app.route('/', methods=['GET','POST'])
def home():
    score = None
    reasons = []
    link = ""
    if request.method == 'POST':
        link = request.form.get('url','')
        if link:
            score, reasons = check_link(link)
    color = "#00ff88" if score is not None and score < 30 else "#ffcc00" if score is not None and score < 60 else "#ff3b3b"
    reasons_html = "<br>".join([f"<p>{r}</p>" for r in reasons])
    result_html = f'<h2 style="color:{color};">Risk Score: {score}/100</h2>{reasons_html}' if score is not None else ''
    return f"""
    <div style="direction:rtl; text-align:center; font-family:Arial; background:#0a1929; color:white; min-height:100vh; padding:20px;">
    <h2>SOC - Link Checker</h2>
    <form method="POST">
    <input name="url" value="{link}" placeholder="https://example.com" style="width:90%; padding:12px; border-radius:10px; border:none; text-align:center;">
    <br><br>
    <button style="background:#ff3b3b; color:white; padding:12px 30px; border:none; border-radius:10px; font-size:18px;">Check</button>
    </form><br>{result_html}</div>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
