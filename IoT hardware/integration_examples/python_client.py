#!/usr/bin/env python3
"""
AgroSphere AI - Python Integration Example
==========================================
Example client to consume IoT sensor data from the API
"""

import requests
import time
from datetime import datetime

# Configuration
API_BASE_URL = "https://mamie-prognosticable-chadwick.ngrok-free.dev"

class AgroSphereClient:
    """Client for AgroSphere AI IoT API"""
    
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get_latest_data(self):
        """Get the latest sensor reading"""
        try:
            response = requests.get(f"{self.base_url}/api/sensor-data", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: HTTP {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            return None
    
    def get_history(self):
        """Get historical sensor data"""
        try:
            response = requests.get(f"{self.base_url}/api/sensor-history", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            return None
    
    def check_health(self):
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            return response.status_code == 200
        except:
            return False


def analyze_crop_risk(data):
    """Analyze crop risk based on sensor data"""
    risk_factors = []
    risk_score = 0
    
    temp = data['temperature_celsius']
    moisture = data['soil_moisture_percent']
    
    # Temperature risk
    if temp > 35:
        risk_factors.append(f"High temperature: {temp}°C (Heat stress)")
        risk_score += 50
    elif temp > 30:
        risk_factors.append(f"Elevated temperature: {temp}°C")
        risk_score += 20
    
    # Moisture risk
    if moisture < 20:
        risk_factors.append(f"Low soil moisture: {moisture}% (Drought stress)")
        risk_score += 50
    elif moisture < 40:
        risk_factors.append(f"Below optimal moisture: {moisture}%")
        risk_score += 20
    
    # Determine risk level
    if risk_score >= 70:
        risk_level = "CRITICAL"
    elif risk_score >= 40:
        risk_level = "HIGH"
    elif risk_score >= 20:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    return {
        'risk_level': risk_level,
        'risk_score': risk_score,
        'risk_factors': risk_factors,
        'recommendation': get_recommendation(risk_level)
    }


def get_recommendation(risk_level):
    """Get action recommendation based on risk level"""
    recommendations = {
        'CRITICAL': 'Immediate action required: Consider early harvest or emergency irrigation',
        'HIGH': 'Monitor closely: Prepare contingency plans',
        'MEDIUM': 'Watch conditions: Adjust irrigation schedule',
        'LOW': 'Normal operations: Continue monitoring'
    }
    return recommendations.get(risk_level, 'No recommendation')


def calculate_price_adjustment(data):
    """Calculate price adjustment based on crop stress"""
    base_price = 100.0
    adjustment = 0.0
    
    temp = data['temperature_celsius']
    moisture = data['soil_moisture_percent']
    
    # Heat stress increases prices (reduced supply)
    if temp > 35:
        adjustment += 15.0
    elif temp > 30:
        adjustment += 5.0
    
    # Drought stress increases prices
    if moisture < 20:
        adjustment += 10.0
    elif moisture < 40:
        adjustment += 3.0
    
    adjusted_price = base_price * (1 + adjustment / 100)
    
    return {
        'base_price': base_price,
        'adjustment_percent': adjustment,
        'adjusted_price': round(adjusted_price, 2),
        'reason': 'Supply reduction due to crop stress' if adjustment > 0 else 'Normal conditions'
    }


def monitor_realtime():
    """Monitor sensors in real-time"""
    client = AgroSphereClient(API_BASE_URL)
    
    print("=" * 70)
    print("AgroSphere AI - Real-Time Monitoring")
    print("=" * 70)
    print(f"API: {API_BASE_URL}")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()
    
    try:
        while True:
            data = client.get_latest_data()
            
            if data:
                # Display sensor data
                print(f"\n{'='*70}")
                print(f"Timestamp: {data['timestamp']}")
                print(f"Node ID: {data['node_id']}")
                print(f"Temperature: {data['temperature_celsius']}°C")
                print(f"Humidity: {data['humidity_percent']}%")
                print(f"Soil Moisture: {data['soil_moisture_percent']}%")
                print(f"Status: {data['status']}")
                
                # Analyze risk
                risk = analyze_crop_risk(data)
                print(f"\nRisk Analysis:")
                print(f"  Level: {risk['risk_level']} (Score: {risk['risk_score']})")
                if risk['risk_factors']:
                    print(f"  Factors:")
                    for factor in risk['risk_factors']:
                        print(f"    - {factor}")
                print(f"  Recommendation: {risk['recommendation']}")
                
                # Calculate price impact
                price = calculate_price_adjustment(data)
                print(f"\nPrice Impact:")
                print(f"  Base Price: ${price['base_price']}")
                print(f"  Adjustment: +{price['adjustment_percent']}%")
                print(f"  Adjusted Price: ${price['adjusted_price']}")
                print(f"  Reason: {price['reason']}")
                
                if data['market_warning']:
                    print(f"\n⚠️  MARKET WARNING ACTIVE!")
            else:
                print("⚠️  Failed to fetch data")
            
            time.sleep(5)  # Poll every 5 seconds
    
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped")


def generate_report():
    """Generate a summary report"""
    client = AgroSphereClient(API_BASE_URL)
    
    print("=" * 70)
    print("AgroSphere AI - Sensor Report")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # Get latest data
    latest = client.get_latest_data()
    if latest:
        print("Latest Reading:")
        print(f"  Temperature: {latest['temperature_celsius']}°C")
        print(f"  Humidity: {latest['humidity_percent']}%")
        print(f"  Soil Moisture: {latest['soil_moisture_percent']}%")
        print(f"  Status: {latest['status']}")
        print()
    
    # Get history
    history = client.get_history()
    if history and history['count'] > 0:
        data_points = history['data']
        
        # Calculate averages
        avg_temp = sum(d['temperature_celsius'] for d in data_points) / len(data_points)
        avg_humidity = sum(d['humidity_percent'] for d in data_points) / len(data_points)
        avg_moisture = sum(d['soil_moisture_percent'] for d in data_points) / len(data_points)
        
        print(f"Historical Analysis ({history['count']} readings):")
        print(f"  Average Temperature: {avg_temp:.2f}°C")
        print(f"  Average Humidity: {avg_humidity:.2f}%")
        print(f"  Average Soil Moisture: {avg_moisture:.2f}%")
        print()
        
        # Count warnings
        warnings = sum(1 for d in data_points if d.get('market_warning', False))
        print(f"  Market Warnings: {warnings} ({warnings/len(data_points)*100:.1f}%)")
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "monitor":
            monitor_realtime()
        elif command == "report":
            generate_report()
        elif command == "latest":
            client = AgroSphereClient(API_BASE_URL)
            data = client.get_latest_data()
            if data:
                print(f"Temperature: {data['temperature_celsius']}°C")
                print(f"Humidity: {data['humidity_percent']}%")
                print(f"Soil Moisture: {data['soil_moisture_percent']}%")
                print(f"Status: {data['status']}")
        else:
            print("Unknown command")
            print("Usage: python python_client.py [monitor|report|latest]")
    else:
        print("AgroSphere AI - Python Client")
        print()
        print("Usage:")
        print("  python python_client.py monitor   # Real-time monitoring")
        print("  python python_client.py report    # Generate report")
        print("  python python_client.py latest    # Get latest reading")
