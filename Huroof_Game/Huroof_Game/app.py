import random
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# بنك الأسئلة المبدئي الذكي
QUESTIONS_BANK = {
    "أ": [{"q": "من الجمال", "a": "الحسن"}],
    "ب": [{"q": "ثاني حروف الهجاء", "a": "باء"}],
    "ت": [{"q": "عاصمة اليابان", "a": "طوكيو"}],
    "ث": [{"q": "يرتديها الملوك على رؤوسهم", "a": "تاج"}],
    "ج": [{"q": "مخلوقات غيبية خلقها الله من نار", "a": "الجن"}],
    "ح": [{"q": "الحيوان المعروف بسفينة الصحراء", "a": "الجمل"}],
    "خ": [{"q": "مادة تصنع منها الطاولات والكبائن", "a": "الخشب"}],
    "د": [{"q": "عاصمة المملكة العربية السعودية", "a": "الرياض"}],
    "ذ": [{"q": "عضو في الجسم نذوق به الطعام", "a": "اللسان"}],
    "ر": [{"q": "من شهور السنة الهجرية يأتي بعد شعبان", "a": "رمضان"}],
    "ز": [{"q": "كوكب يشتهر بحلقاته الجميلة حوله", "a": "زحل"}],
    "س": [{"q": "نجم تشرق منه الأرض بالدفء والنور", "a": "الشمس"}],
    "ش": [{"q": "حيوان مفترس يلقب بملك الغابة", "a": "الأسد"}],
    "ص": [{"q": "صوت المؤذن الذي يدعو به للصلاة", "a": "الأذان"}],
    "ض": [{"q": "اللغة العربية هي لغة الـ...", "a": "الضاد"}],
    "ط": [{"q": "طائر جارح قوي النظر ورمز الشجاعة", "a": "الصقر"}],
    "ظ": [{"q": "تأتي بعد العصر وقبل المغرب", "a": "المغرب"}],
    "ع": [{"q": "عاصمة جمهورية مصر العربية", "a": "القاهرة"}],
    "غ": [{"q": "طائر ذكي أسود اللون ورد في القرآن الكريم", "a": "الغراب"}],
    "ف": [{"q": "أكبر الثدييات ويعيش في المحيطات", "a": "الحوت"}],
    "ق": [{"q": "جرم سماوي يضيء ليل الأرض", "a": "القمر"}],
    "ك": [{"q": "أكبر قارات العالم من حيث المساحة والسكان", "a": "آسيا"}],
    "ل": [{"q": "معدن نفيس أصفر اللون تحبه النساء", "a": "الذهب"}],
    "م": [{"q": "المدينة المقدسة التي بها المسجد الحرام", "a": "مكة المكرمة"}],
    "ن": [{"q": "الحشرة النشيطة التي تجمع العسل", "a": "النحلة"}],
    "هـ": [{"q": "بناء شامخ مشهور في الجيزة بمصر", "a": "الهرم"}],
    "و": [{"q": "عاصمة فرنسا ومدينة النور", "a": "باريس"}],
    "ي": [{"q": "اليوم الذي يجتمع فيه المسلمون لصلاة الظهر خطبة", "a": "الجمعة"}]
}

LETTERS_LIST = list(QUESTIONS_BANK.keys())

# حالة اللعبة الافتراضية
state = {
    "team1_name": "الفريق الأحمر",
    "team2_name": "الفريق الأخضر",
    "grid_size": 5,
    "board": {}
}

def generate_board(size):
    board = {}
    used_letters = []
    for r in range(size):
        for c in range(size):
            available = [L for L in LETTERS_LIST if L not in used_letters]
            if not available:
                used_letters = []
                available = LETTERS_LIST
            chosen_letter = random.choice(available)
            used_letters.append(chosen_letter)
            
            q_pool = QUESTIONS_BANK.get(chosen_letter, [{"q": "لا يوجد سؤال حالياً", "a": "-"}])
            q_item = random.choice(q_pool)
            
            cell_id = f"{r},{c}"
            board[cell_id] = {
                "letter": chosen_letter,
                "question": q_item["q"],
                "answer": q_item["a"],
                "color": "none"
            }
    return board

state["board"] = generate_board(5)

@app.route('/')
def player_page():
    return render_template('player.html', state=state)

@app.route('/admin')
def admin_page():
    return render_template('admin.html', state=state)

@app.route('/api/get_state')
def get_state():
    return jsonify(state)

@app.route('/api/click_cell', methods=['POST'])
def click_cell():
    data = request.json
    cell_id = data.get('cell_id')
    color = data.get('color')
    if cell_id in state["board"]:
        state["board"][cell_id]["color"] = color
    return jsonify({"success": True})

@app.route('/api/update_settings', methods=['POST'])
def update_settings():
    data = request.json
    state["team1_name"] = data.get('team1_name', state["team1_name"])
    state["team2_name"] = data.get('team2_name', state["team2_name"])
    new_size = int(data.get('grid_size', state["grid_size"]))
    if new_size != state["grid_size"]:
        state["grid_size"] = new_size
        state["board"] = generate_board(new_size)
    return jsonify({"success": True})

@app.route('/api/add_to_bank', methods=['POST'])
def add_to_bank():
    data = request.json
    letter = data.get('letter')
    q = data.get('question')
    a = data.get('answer')
    if letter and q and a:
        if letter not in QUESTIONS_BANK:
            QUESTIONS_BANK[letter] = []
        QUESTIONS_BANK[letter].append({"q": q, "a": a})
        state["board"] = generate_board(state["grid_size"])
    return jsonify({"success": True})

@app.route('/api/clear', methods=['POST'])
def clear_board():
    state["board"] = generate_board(state["grid_size"])
    return jsonify({"success": True})

# هذا السطر مهم جداً لمنصة Vercel لكي تتعرف على التطبيق وتدرير اللعبة
app = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)