from my_recommender import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting Flask server on http://127.0.0.1:5001")
    app.run(debug=True, port=5001)