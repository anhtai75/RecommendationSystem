from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from flask_cors import CORS
import os
import json

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Dữ liệu đánh giá người dùng
ratings_dict = {
    "userId": [1, 1, 1, 2, 2, 3, 3, 3, 4, 4],
    "movieId": [101, 102, 103, 101, 104, 102, 103, 105, 101, 105],
    "rating": [5, 4, 3, 5, 4, 4, 2, 5, 3, 4]
}
ratings_df = pd.DataFrame(ratings_dict)

# Đọc dữ liệu phim từ file JSON
with open("static/data/movies.json", "r", encoding="utf-8") as f:
    movies_data = json.load(f)
movies_df = pd.DataFrame(movies_data)

# Xây dựng mô hình gợi ý
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings_df[['userId', 'movieId', 'rating']], reader)
trainset, testset = train_test_split(data, test_size=0.2)
model = SVD()
model.fit(trainset)

# Hàm gợi ý phim cho user (hiển thị nhiều hơn)
def recommend_movies(user_id, num_recommendations=10):  # Đã tăng số lượng phim
    all_movie_ids = movies_df["movieId"].unique()
    watched_movies = ratings_df[ratings_df["userId"] == user_id]["movieId"].values
    not_watched_movies = [m for m in all_movie_ids if m not in watched_movies]
    predictions = [model.predict(user_id, movie_id) for movie_id in not_watched_movies]
    predictions.sort(key=lambda x: x.est, reverse=True)
    recommended_movie_ids = [pred.iid for pred in predictions[:num_recommendations]]
    recommended_movies = movies_df[movies_df["movieId"].isin(recommended_movie_ids)]
    return recommended_movies.to_dict(orient="records")

# Hàm tìm phim theo chủ đề
def get_movies_by_genre(genre):
    # Tìm phim theo thể loại (genre)
    genre_movies = movies_df[movies_df['genre'].str.contains(genre, case=False)]
    return genre_movies.to_dict(orient="records")

# Giao diện chọn user và hiển thị gợi ý
@app.route("/", methods=["GET", "POST"])
def home():
    recommendations = []
    user_id = None
    genre = None
    num_recommendations = 10
    if request.method == "POST":
        user_id = int(request.form.get("user_id", 1))
        genre = request.form.get("genre", "")  # Lấy thể loại người dùng chọn
        num_recommendations = int(request.form.get("num_recommendations", 10))  # Số lượng phim người dùng muốn
        if genre:
            recommendations = get_movies_by_genre(genre)  # Tìm phim theo thể loại
        else:
            recommendations = recommend_movies(user_id, num_recommendations)
    return render_template("index.html", user_id=user_id, recommendations=recommendations, genre=genre, num_recommendations=num_recommendations)

# API JSON
@app.route("/recommend", methods=["GET"])
def get_recommendations():
    user_id = int(request.args.get("user_id", 1))
    num_recommendations = int(request.args.get("num_recommendations", 10))  # Lấy tham số số lượng phim
    recommendations = recommend_movies(user_id, num_recommendations)
    return jsonify({"user_id": user_id, "recommendations": recommendations})

# API JSON cho phim theo thể loại
@app.route("/genre", methods=["GET"])
def get_movies_by_genre_api():
    genre = request.args.get("genre", "")
    recommendations = get_movies_by_genre(genre)
    return jsonify({"genre": genre, "recommendations": recommendations})

if __name__ == "__main__":
    app.run(debug=True)