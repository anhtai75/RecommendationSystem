from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Dữ liệu phim và đánh giá giả lập
ratings_dict = {
    "userId": [1, 1, 1, 2, 2, 3, 3, 3, 4, 4],
    "movieId": [101, 102, 103, 101, 104, 102, 103, 105, 101, 105],
    "rating": [5, 4, 3, 5, 4, 4, 2, 5, 3, 4]
}
movies_dict = {
    "movieId": [101, 102, 103, 104, 105, 106, 107],
    "title": ["Marvel", "Interstellar", "The Matrix", "Avatar", "Titanic","Magic Mike’s Last Dance","Bộ 4 báo thủ"]
}
ratings_df = pd.DataFrame(ratings_dict)
movies_df = pd.DataFrame(movies_dict)

# Xây dựng mô hình gợi ý
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings_df[['userId', 'movieId', 'rating']], reader)
trainset, testset = train_test_split(data, test_size=0.2)
model = SVD()
model.fit(trainset)

def recommend_movies(user_id, num_recommendations=3):
    all_movie_ids = movies_df["movieId"].unique()
    watched_movies = ratings_df[ratings_df["userId"] == user_id]["movieId"].values
    not_watched_movies = [m for m in all_movie_ids if m not in watched_movies]
    predictions = [model.predict(user_id, movie_id) for movie_id in not_watched_movies]
    predictions.sort(key=lambda x: x.est, reverse=True)
    recommended_movie_ids = [pred.iid for pred in predictions[:num_recommendations]]
    recommended_movies = movies_df[movies_df["movieId"].isin(recommended_movie_ids)]
    return recommended_movies.to_dict(orient="records")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommend", methods=["GET"])
def get_recommendations():
    user_id = int(request.args.get("user_id", 1))
    recommendations = recommend_movies(user_id)
    return jsonify({"user_id": user_id, "recommendations": recommendations})

if __name__ == "__main__":
    app.run(debug=True)
