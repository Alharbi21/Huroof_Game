import os
import random
import json
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# الربط التلقائي بقاعدة بيانات Neon السحابية عبر المتغيرات السرية في Vercel
# وإذا لم تكن موجودة (مثل التشغيل المحلي) سيعتمد على قاعدة بيانات مؤقتة
DATABASE_URL = os.environ.get('POSTGRES_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///huroof_local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# بناء الهيكل الذكي لحفظ الغرف والألوان في قاعدة البيانات
class GameRoom(db.Model):
    __tablename__ = 'game_rooms'
    room_id = db.Column(db.String(20), primary_key=True)
    letters_data = db.Column(db.Text, nullable=False) # سنحفظ الألوان هنا بنص JSON متطور

# إنشاء الجداول بداخل Neon تلقائياً عند تشغيل اللعبة
with app.app_context():
    db.create_all()

# تحميل بنك الأسئلة
def load_questions():
    try:
        with open('questions.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading questions: {e}")
        return []

QUESTIONS_BANK = load_questions()

# دالة لتوليد مصفوفة الحروف الافتراضية باللون الرمادي
def get_default_letters():
    alphabet = ["أ", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "هـ", "و", "ي"]
    return {letter: "gray" for letter in alphabet}

@app.route('/')
def index():
    return render_template('index.html')

# 1. إنشاء غرفة لعب جديدة تماماً برمز عشوائي
@app.route('/api/create_room', methods=['POST'])
def create_room():
    room_id = str(random.randint(1000, 9999))
    default_letters = get_default_letters()
    
    # حفظ الغرفة الجديدة في قاعدة البيانات السحابية
    new_room = GameRoom(room_id=room_id, letters_data=json.dumps(default_letters))
    db.session.add(new_room)
    db.session.commit()
    
    return jsonify({"room_id": room_id, "letters": default_letters})

# 2. دخول اللاعب أو الصديق إلى غرفة موجودة مسبقاً بجلب ألوانها الحالية
@app.route('/api/get_room/<room_id>', methods=['GET'])
def get_room(room_id):
    room = GameRoom.query.filter_by(room_id=room_id).first()
    if room:
        return jsonify({"exists": True, "letters": json.loads(room.letters_data)})
    return jsonify({"exists": False, "message": "المعذرة، هذه الغرفة غير موجودة!"})

# 3. تحديث لون حرف معين بداخل الغرفة (سواء أحمر أو أزرق) وحفظه فوراً في السحاب
@app.route('/api/update_letter', methods=['POST'])
def update_letter():
    data = request.json
    room_id = data.get('room_id')
    letter = data.get('letter')
    color = data.get('color')
    
    room = GameRoom.query.filter_by(room_id=room_id).first()
    if room:
        current_letters = json.loads(room.letters_data)
        if letter in current_letters:
            current_letters[letter] = color
            room.letters_data = json.dumps(current_letters)
            db.session.commit() # حفظ أبدي في السيرفر!
            return jsonify({"success": True, "letters": current_letters})
            
    return jsonify({"success": False, "message": "فشل تحديث بيانات الغرفة"})

# 4. سحب سؤال عشوائي من بنك الأسئلة المدمج
@app.route('/api/get_question', methods=['GET'])
def get_question():
    if not QUESTIONS_BANK:
        return jsonify({"error": "بنك الأسئلة فارغ!"})
    random_question = random.choice(QUESTIONS_BANK)
    return jsonify(random_question)

if __name__ == '__main__':
    app.run(debug=True)