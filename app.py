from flask import Flask, render_template, request, jsonify
import pickle
import requests

app = Flask(__name__)

# Load the movie data and similarity scores
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data['poster_path']
    full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return full_path

def details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    data_details = {"date": data["release_date"], "revenue": data["revenue"], "runtime": data["runtime"]}
    return data_details

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    movie_details = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        movie_details.append(details(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters, movie_details

@app.route('/')
def home():
    movie_titles = movies['title'].tolist()  # Get movie titles for the dropdown
    return render_template('index.html', movies=movie_titles)

@app.route('/recommend', methods=['POST'])
def recommend_movies():
    data = request.get_json()  # Use get_json to parse JSON data
    movie_name = data['movie']
    recommended_movie_names, recommended_movie_posters, movie_details = recommend(movie_name)
    recommendations = []
    for i in range(5):
        recommendations.append({
            'name': recommended_movie_names[i],
            'poster': recommended_movie_posters[i],
            'details': movie_details[i]
        })
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
