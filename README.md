# Recipe Sharing Platform

This project is a Recipe Sharing Platform web application built using Flask and SQLAlchemy.

## Installation

### Prerequisites

- Python 3.x
- Virtual environment (optional but recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/recipe-platform.git
   ```
2. Navigate to the project directory:
   ```bash
   cd recipe-platform
   ```
3. (Optional) Create a virtual environment:
   ```bash
   pipenv shell
   ```
4. Install dependencies:
   ```bash
   pipenv install -r requirements.txt
   ```
5. Set up the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

### Usage

1. Start the Flask server:
   ```bash
   flask run
   ```
2. Access the application in your browser at `http://localhost:9999`.

## Project Structure

- `app`: Contains the main application code.
- `static`: Static assets such as CSS, JS, and images.
- `templates`: HTML templates used in the application.
- `uml`: UML diagrams of application
- ...

## Features

- User signup and login with secure authentication
- Add recipe
- Explore recipes with user preference recommendations
- Recipe ratings and comments feedback
- Live feedback to recipe creators
