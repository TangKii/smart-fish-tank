from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime
import os
import random

app = Flask(__name__)

# 数据库初始化
def init_db():
    conn = sqlite3.connect('fish_tank.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS feeding_records
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# 主页
@app.route('/')
def index():
    # 模拟温度数据
    temperature = 20.3
    max_temp = 21.5
    min_temp = 19.0
    
    return render_template('index.html', 
                         temperature=temperature,
                         max_temp=max_temp,
                         min_temp=min_temp)

# 灯效模式页面
@app.route('/lighting-modes')
def lighting_modes():
    return render_template('lighting_modes.html')

# 全局变量存储喂食记录
feeding_records = [
    {
        "time": "2024-01-20 08:30",
        "food_type": "鱼粮",
        "amount": "5g",
        "status": "成功"
    },
    {
        "time": "2024-01-19 19:00",
        "food_type": "鱼粮",
        "amount": "5g",
        "status": "成功"
    },
    {
        "time": "2024-01-19 08:30",
        "food_type": "鱼粮",
        "amount": "5g",
        "status": "成功"
    },
    {
        "time": "2024-01-18 19:00",
        "food_type": "鱼粮",
        "amount": "5g",
        "status": "失败"
    }
]

# 喂食记录页面
@app.route('/feeding-records')
def feeding_records_page():
    return render_template('feeding_records.html', records=feeding_records)

# 喂食记录页面（数据库版）
@app.route('/feeding-records-db')
def feeding_records_db():
    conn = sqlite3.connect('fish_tank.db')
    c = conn.cursor()
    c.execute('SELECT timestamp FROM feeding_records ORDER BY timestamp DESC')
    records = c.fetchall()
    conn.close()
    return render_template('feeding_records.html', records=records)

# 添加喂食记录
@app.route('/add-feeding-record', methods=['POST'])
def add_feeding_record():
    conn = sqlite3.connect('fish_tank.db')
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO feeding_records (timestamp) VALUES (?)', (now,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'timestamp': now})

# 喂食功能
@app.route('/feed', methods=['POST'])
def feed():
    # 模拟喂食操作
    success = random.random() > 0.1  # 90% 成功率
    
    # 创建新的喂食记录
    new_record = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "food_type": "鱼粮",
        "amount": "5g",
        "status": "成功" if success else "失败"
    }
    
    # 添加到记录列表的开头
    feeding_records.insert(0, new_record)
    
    # 返回操作结果
    return jsonify({
        "success": success,
        "message": "喂食成功" if success else "喂食失败",
        "record": new_record
    })

# 水流控制路由
@app.route('/set_water_flow', methods=['POST'])
def set_water_flow():
    try:
        data = request.get_json()
        level = data.get('level')
        
        # 这里可以添加实际的水流控制逻辑
        # 目前只是模拟返回成功
        return jsonify({
            'success': True,
            'message': f'水流已设置为{level}档',
            'level': level
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '设置水流失败',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
