## **Arithmetic Practice App**


### Author : **Afshan Afridi**
### AfridiGitHub Username: Afshan08
#### edX Username:afshan afridi 
#### City & Country: Karachi, Pakistan
##### Date of Submission: 16/03/2025

## **Overview**

The Arithmetic Practice App is a web-based platform designed to help users improve their arithmetic skills through structured practice. The application allows users to create an account, log in, and track their progress. One of its unique features is its adaptive learning approach—questions that users answer incorrectly appear more frequently to reinforce learning.

The app is built using Flask, SQLAlchemy (with SQLite), HTML/CSS, and JavaScript. It follows a full-stack development approach and implements user authentication, a personalized dashboard, and interactive question-generation mechanics.

## **Features**

##### *User Authentication*: 
Secure login and registration using Flask.

##### *Personalized Dashboard:*
 Tracks user progress and suggests questions based on past mistakes.

##### *Question Generation:*
Dynamically generates arithmetic problems for addition, subtraction, multiplication, and division.

##### *Progress Tracking:*
Stores user performance data in a database and makes the dashboard accordingly and give suggestions as well.

##### *Interactive Practice Page:*
Provides instant feedback on answers.

##### *Database Integration:*
Uses SQLAlchemy with SQLite to store user data and question history.

##### *Modern UI:*
Designed for a seamless user experience with HTML, CSS, and JavaScript.

# **File Structure**

## *Backend (Flask)*

app.py: The main Flask application file that handles routing, authentication, and API endpoints.


##### *maths_game.db:*
SQLite database file that stores user progress and authentication details.

## *Frontend (HTML, CSS, JavaScript)*

static/: Contains CSS files.

templates/: Stores HTML templates for different pages (index, login, register, practice, dashboard).

static/css/style.css: Styles the application for a clean and modern look.

## **User Authentication**

Users register and log in securely using Flask's session management.

Passwords are hashed before storing them in the database.

## **Question Generation & Practice Mechanics**

The app dynamically generates arithmetic problems.

Incorrectly answered questions appear more frequently for better learning reinforcement.

Users receive real-time feedback on their answers.

## **Design Choices & Challenges**

Flask vs. Django: Flask was chosen over Django due to its lightweight nature, making it easier to develop and maintain.

SQLAlchemy with SQLite: SQLAlchemy was used for database management, offering flexibility for potential future scalability.

Session Management: Used Flask’s built-in session handling to manage user logins without requiring external authentication services.

Frontend & UI: Balancing aesthetics with functionality was a challenge, but the final UI provides a smooth user experience.

## Installation & Setup

Prerequisites

Ensure you have Python and Flask installed:

pip install flask flask_sqlalchemy flask_login

Run the Application

python app.py

Then, open your browser and navigate to http://127.0.0.1:5000/

## **Future Improvements**

Implementing a leaderboard to introduce a competitive element.

Adding difficulty levels based on user proficiency.

Supporting additional arithmetic operations like exponentiation and fractions.

Implementing a mobile-responsive design.

Adding an API for third-party integrations.

## **Conclusion**

The Arithmetic Practice App is designed to provide an interactive and adaptive learning experience for users aiming to improve their arithmetic skills. With a strong focus on user engagement, real-time feedback, and progress tracking, this project showcases the power of full-stack web development. Future enhancements will make it even more robust and user-friendly.