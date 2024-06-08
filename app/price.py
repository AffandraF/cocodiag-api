from flask import Blueprint, jsonify
from selenium.webdriver.common.by import By
import undetected_chromedriver.v2 as uc
from app.auth import jwt_required

price_bp = Blueprint('price_bp', __name__)

def get_data():
    try:
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(options=options)

        url = "https://infopangan.jakarta.go.id/publik/dashboard/23"
        driver.get(url)

        date = driver.find_element(By.ID, "avg_tanggal")
        date = date.text

        price = driver.find_element(By.ID, "avg_value")
        price = price.text

        region = driver.find_element(By.ID, "avg_object")
        region = region.text        

        driver.quit()

        response = {
            "date": date,
            "price": price,            
            "region": region
        }

        return response

    except Exception as e:
        return {"error": str(e)}

@price_bp.route('/getPrice', methods=['GET'])
@jwt_required()
def send_data():
    data = get_data()

    if "error" in data:
        return jsonify(data), 500  
    return jsonify(data)