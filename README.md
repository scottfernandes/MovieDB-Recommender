# MovieDB-Recommender
1. A Content-based Movie Recommender with some additional features like Sentiment Analysis of Reviews and many more.
2. Makes use of nextAuth for google and github authentication.
3. Create a .env file in 'movierecom' folder and the contents shown below
4. Uses TMDB API for fetching details like poster,cast details,etc.
5. Make sure to create your account on TMDB and use your API Key. Edit the variable in the server.py file.
6. In the src/app folder, create this "api/auth/[...nextAuth]" and in this directory add the route.js file


# Contents to be added in .env file
NEXTAUTH_URL='http://localhost:3000'

GITHUB_ID=''
GITHUB_SECRET=''

GOOGLE_ID=''
GOOGLE_SECRET=''

# Frontend
Used NextJS and ShadcnUI for frontend

Perform the following in the terminal:-
1. cd movierecom
2. npm install
3. npm run dev
   
# Backend
Used Flask for connecting with the ML Model and as a backend.
Run the server.py file.

# Database
Uses MongoDB for storing user data

