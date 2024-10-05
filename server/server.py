from flask import Flask, request, jsonify, make_response, redirect
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, 
    get_jwt_identity, jwt_required, set_access_cookies, 
    set_refresh_cookies, unset_jwt_cookies
)
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Message, Mail
import warnings
from pymongo import MongoClient
import secrets
from datetime import timedelta
from proper import *
import logging
warnings.filterwarnings('ignore',category=pd.errors.SettingWithCopyWarning)
logging.basicConfig(level=logging.INFO,  
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('app.log'), 
                        logging.StreamHandler()  
                    ])
app = Flask(__name__)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
mail = Mail(app)


CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

app.config['JWT_SECRET_KEY'] = 'Scout2546'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=30)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['MAIL_SERVER'] = 'smtp.example.com' 
app.config['MAIL_PORT'] = 587  
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'scottfernandes3586@gmail.com'
app.config['MAIL_PASSWORD'] = 'gzhs mmlr rkkd jbnl'
app.config['MAIL_DEFAULT_SENDER'] = 'scottfernandes3586@gmail.com'

client = MongoClient('mongodb://localhost:27017')
db = client['MovieDB']

def generate_secure_token(length=32):
    return secrets.token_hex(length)


df = pd.read_csv('server\\TMDB_Final.csv')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        body = request.json
        name = body.get('name')
        email = body.get('email')
        password = body.get('password', None)  # Use .get() to make password optional
        provider = body.get('provider', 'credentials')  # Default to credentials

        # Check if the user already exists in the database
        if not db['Users'].find_one({"email": email}):
            if provider == 'credentials':
                # If using credentials, ensure a password is provided
                if not password:
                    return jsonify({'message': 'Password is required for credentials signup', 'success': False}), 400
                
                # Hash the password
                pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            elif provider in ['google','github']:
                # For OAuth providers, password is optional (can be set to None)
                pw_hash = None
            
            # Insert user into the database
            db['Users'].insert_one({
                "name": name,
                "email": email,
                "password": pw_hash,  # This will be None for OAuth
                "provider": provider,  # Store the provider (e.g., 'google', 'github', 'credentials')
                "image": body.get('image')  # Optional: Store user profile image if provided
            })
            return jsonify({'success': True}), 200
        else: 
            return jsonify({
                'message': 'An account already exists with this email, try logging in.',
                'success': False
            }), 400

    # Handling GET requests to retrieve user data
    if request.method == 'GET':
        user_email = request.args.get('user_email')
        all_data = db['Users'].find_one({"email":user_email})
        if not all_data:
            return jsonify({'message':'User does not exist','user':None}),200
        data_json = {"id": str(all_data['_id']), "name": all_data['name'], "email": all_data['email'], "provider": all_data['provider'],"image":all_data['image']}
        print(data_json)
        return jsonify({"user":data_json})

@app.route('/autocomplete', methods=['GET'])
def autocom():
    query = request.args.get('query', '')
    movies = df['title'].tolist()
    
    if query:
        movies = [movie for movie in movies if query.lower() in movie.lower()]
    
    return jsonify({'movies': movies[:13]})


@app.route('/login', methods=['POST'])
def login():
    try:
        body = request.json
        email = body.get('email')
        password = body.get('password', None)
        provider = body.get('provider')
        print(provider)
        if provider == 'credentials':
            if not email or not password:
                return jsonify({'message': 'Invalid request. Please provide both email and password.'}), 400

            user = db['Users'].find_one({"email": email})
            
            if user and bcrypt.check_password_hash(user['password'], password):
                logging.info(f'User {email} logged in successfully via credentials')
                response = make_response(jsonify({'email': email, 'is_Auth': True}))
                return response, 200
            else:
                logging.warning(f'Failed login attempt for {email}')
                return jsonify({'message': 'Invalid email or password'}), 401

        # Case 2: Other provider (Google, etc.)
        elif provider and provider != 'credentials':
            user = db['Users'].find_one({"email": email})
            print(user)
            if user:
                if user['provider']=='credentials':
                    logging.warning(f'Failed login attempt for {email} via {provider}')
                    return jsonify({'message': 'User has credentials'}), 404
                else:
                    logging.info(f'User {email} logged in successfully via {provider}')
                    return jsonify({'message': 'Logged in successfully', 'provider': provider}), 200

        # Case 3: Invalid provider
        else:
            return jsonify({'message': 'Invalid provider'}), 400

    except Exception as e:
        logging.error(f"Login failed due to an error: {str(e)}")
        return jsonify({'message': 'Internal Server Error', 'error': str(e)}), 500

@app.route("/watchlist", methods=["GET","POST","DELETE"])
def save_movie():
   
   if request.method=='POST':
        data = request.json
        username = data.get("username")
        title = data.get("title")
        poster = data.get("poster")
        movie_id = get_movie_id(title)
        print(username)
        if username and title and poster:
            user = db['Users'].find_one({"email": username})

            if any(movie['id'] == movie_id for movie in user.get('movies', [])):
                return jsonify({"message": "Movie already in watchlist"}), 400
            
            if user and title and poster:
                db['Users'].update_one(
                {"email": username},
                {"$push": {"movies": {"id":movie_id,"title": title, "poster": poster,"saved":True}}},
                    )
           

            return jsonify({"message": "Movie saved successfully","data":[username,title,poster]}), 200
        else:
            return jsonify({"error": "Missing data"}), 400

    
   if request.method=='GET':
       username = request.args.get('username')
       if username:
            user = db['Users'].find_one({"email": username}, {"_id": 0, "movies": 4})

            if user:
                movies = user.get('movies', [])      
                if len(movies)==0 or not movies:               
                    print('No movies found') 
                    return jsonify({"message":"There are no movies in your watchlist. Start adding them and have your own personalized watchlist."}),404
                else:
                    return jsonify({"movies":movies})
            else:
                print('No')
                return jsonify({'message':"There are no movies in your watchlist. Start adding them and have your own personalized watchlist."}),404      
       else:
            return jsonify({"error": "Username not provided"}),401

   if request.method=='DELETE':
       
       username=request.args.get('username')
       titlemov = request.args.get('title')
       poster = request.args.get('poster') 
       print(username,titlemov,poster) 
       if username:
            user = db['Users'].find_one({"email": username}, {"_id": 0, "movies": 4})

            if user:
                movies = user.get('movies', [])
                filtered_movies = [movie for movie in movies if movie['id'] != get_movie_id(titlemov)]  # Filter movies
                print(filtered_movies)
                if filtered_movies!= movies:
                    db['Users'].update_one(
                        {'email':username},
                        {'$set':{"movies":filtered_movies}}
                    )
                    if len(movies)==0:  
                        return jsonify({'message':"There are no movies in your watchlist. Start adding them and have your own personalized watchlist."}),404
                    
                return jsonify({"message": "Movie removed successfully","data":filtered_movies}), 200

            
       else:
            return jsonify({"error": "Username not provided"}),400
       

@app.route('/recom', methods=['POST'])
def recom():
       try:
            data = request.json
            if 'movie_name' in data:  
                movie_name = data['movie_name']
                movies = recommend(movie_name)
                return jsonify(movies)
            else:
                return jsonify({'error': 'Invalid request. Please provide a valid movie name.'}), 400
        
       except Exception as e:
           return jsonify({'error':'Oops! An error occured with the server. Try restarting'}),404
    
@app.route('/castdetails', methods=['GET', 'POST'])
def show():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Invalid content type'}), 400
    


    if request.method=='POST':
        data=request.json
        if 'castname' in data:
            cast_name = data['castname']
            details = cast_details(cast_name)
            print(details)
            return jsonify(details)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
