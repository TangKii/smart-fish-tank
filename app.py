from flask import Flask, render_template, jsonify, request
import random
import math
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

app = Flask(__name__)

# 数据库配置
engine = create_engine('sqlite:///fish_tank.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

# 数据模型
class SensorData(Base):
    __tablename__ = 'sensor_data'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    temperature = Column(Float, nullable=False)
    ph_level = Column(Float, nullable=False)
    water_level = Column(Float, nullable=False)

    def to_dict(self):
        return {
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M'),
            'temperature': round(self.temperature, 2),
            'ph_level': round(self.ph_level, 2),
            'water_level': self.water_level
        }

# 创建数据库表
Base.metadata.create_all(engine)

# 模拟传感器数据类
class FishTankSensor:
    def __init__(self):
        self.temperature = 25.0
        self.ph_level = 7.0
        self.water_level = 100
        self.fish_count = 5
        self.last_update = datetime.now()
        self.daily_temp_cycle = 0
        self._initialize_historical_data()
        self.lighting = {
            'state': False,
            'rgb': {'r': 255, 'g': 255, 'b': 255}
        }
        self.aeration = False
        self.water_circulation = 0  # 0: 关闭, 1: 低速, 2: 中速, 3: 高速

    def _initialize_historical_data(self):
        session = Session()
        if session.query(SensorData).count() == 0:
            # 生成过去7天的历史数据
            current_time = datetime.now()
            for days in range(7, -1, -1):
                for hour in range(24):
                    for i in range(0, 60, 5):  # 每5分钟一条数据
                        past_time = current_time - timedelta(days=days, hours=hour, minutes=i)
                        self.last_update = past_time
                        data = SensorData(
                            timestamp=past_time,
                            temperature=self.get_temperature(),
                            ph_level=self.get_ph_level(),
                            water_level=self.water_level
                        )
                        session.add(data)
            session.commit()
        session.close()

    def get_temperature(self):
        current_time = datetime.now()
        time_diff = (current_time - self.last_update).total_seconds()
        
        self.daily_temp_cycle = (self.daily_temp_cycle + time_diff / 86400) % 1
        day_night_variation = math.sin(2 * math.pi * self.daily_temp_cycle) * 2
        random_variation = random.uniform(-0.3, 0.3)
        drift = math.sin(time_diff / 3600) * 0.5
        
        self.temperature = 25.0 + day_night_variation + random_variation + drift
        self.last_update = current_time
        
        return round(self.temperature, 0)

    def get_ph_level(self):
        self.ph_level += random.uniform(-0.2, 0.2)
        self.ph_level = max(6.0, min(8.0, self.ph_level))
        return round(self.ph_level, 2)

    def log_data(self):
        current_time = datetime.now()
        current_data = {
            'timestamp': current_time.strftime('%Y-%m-%d %H:%M'),
            'temperature': self.get_temperature(),
            'ph_level': self.get_ph_level(),
            'water_level': self.water_level
        }
        
        # 保存到数据库
        session = Session()
        data = SensorData(
            timestamp=current_time,
            temperature=current_data['temperature'],
            ph_level=current_data['ph_level'],
            water_level=current_data['water_level']
        )
        session.add(data)
        session.commit()
        session.close()
        
        return current_data

    def generate_health_alert(self):
        alerts = []
        if self.temperature < 22 or self.temperature > 28:
            alerts.append("Temperature outside optimal range!")
        if self.ph_level < 6.5 or self.ph_level > 7.5:
            alerts.append("pH level is unstable!")
        if self.water_level < 50:
            alerts.append("Low water level detected!")
        return alerts

    def get_historical_data(self, start_date=None, end_date=None):
        session = Session()
        query = session.query(SensorData)
        
        if start_date:
            query = query.filter(SensorData.timestamp >= start_date)
        if end_date:
            query = query.filter(SensorData.timestamp <= end_date)
            
        # 如果没有指定日期，返回最近1小时的数据
        if not start_date and not end_date:
            start_date = datetime.now() - timedelta(hours=1)
            query = query.filter(SensorData.timestamp >= start_date)
        
        data = query.order_by(SensorData.timestamp).all()
        session.close()
        
        return [record.to_dict() for record in data]

    def set_lighting(self, state, r=None, g=None, b=None):
        """控制RGB照明"""
        self.lighting['state'] = state
        if r is not None:
            self.lighting['rgb']['r'] = max(0, min(255, int(r)))
        if g is not None:
            self.lighting['rgb']['g'] = max(0, min(255, int(g)))
        if b is not None:
            self.lighting['rgb']['b'] = max(0, min(255, int(b)))
        return self.lighting

    def set_aeration(self, state):
        """控制打氧"""
        self.aeration = bool(state)
        return self.aeration

    def set_water_circulation(self, level):
        """控制水循环"""
        self.water_circulation = max(0, min(3, int(level)))
        return self.water_circulation

    def get_status(self):
        """获取所有状态"""
        return {
            'lighting': self.lighting,
            'aeration': self.aeration,
            'water_circulation': self.water_circulation
        }

# 初始化传感器
fish_tank = FishTankSensor()

@app.route('/')
def index():
    current_data = fish_tank.log_data()
    alerts = fish_tank.generate_health_alert()
    historical_data = fish_tank.get_historical_data()
    
    return render_template('index.html', 
                         temperature=current_data['temperature'],
                         ph_level=current_data['ph_level'],
                         water_level=current_data['water_level'],
                         alerts=alerts,
                         historical_data=historical_data)

@app.route('/data')
def get_tank_data():
    current_data = fish_tank.log_data()
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    historical_data = fish_tank.get_historical_data(start_date, end_date)
    
    timestamps = []
    temperatures = []
    ph_levels = []
    
    for data in historical_data:
        timestamps.append(data['timestamp'])
        temperatures.append(data['temperature'])
        ph_levels.append(data['ph_level'])
    
    return jsonify({
        'timestamps': timestamps,
        'temperatures': temperatures,
        'ph_levels': ph_levels
    })

@app.route('/alerts')
def get_alerts():
    alerts = fish_tank.generate_health_alert()
    return jsonify(alerts)

@app.route('/control/lighting', methods=['POST'])
def control_lighting():
    data = request.get_json()
    state = data.get('state', False)
    r = data.get('r')
    g = data.get('g')
    b = data.get('b')
    result = fish_tank.set_lighting(state, r, g, b)
    return jsonify(result)

@app.route('/control/aeration', methods=['POST'])
def control_aeration():
    data = request.get_json()
    state = data.get('state', False)
    result = fish_tank.set_aeration(state)
    return jsonify({'state': result})

@app.route('/control/circulation', methods=['POST'])
def control_circulation():
    data = request.get_json()
    level = data.get('level', 0)
    result = fish_tank.set_water_circulation(level)
    return jsonify({'level': result})

@app.route('/status')
def get_status():
    return jsonify(fish_tank.get_status())

if __name__ == '__main__':
    app.run(debug=True)
