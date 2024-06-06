from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.auth import auth_bp
    from app.prediction import prediction_bp
    from app.price import price_bp
    from app.news import news_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(price_bp)
    app.register_blueprint(news_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)