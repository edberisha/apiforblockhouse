# Financial Data Analysis Backend

## Table of Contents
1. [Introduction]
2. [Technologies Used]
3. [Local Setup]
4. [Running Migrations and Seeding Data]
5. [Deployment on AWS]
   - [Dockerized Setup]
   - [Using AWS RDS]
   - [CI/CD Pipeline]
   - [Handling Environment Variables]
6. [Accessing the Application]
7. [Usage]
8. [Conclusion]

WANT TO TRY THE APP WITHOUT SETTING UP YOUR OWN SYSTEM? GO TO DEPLOYMENT NOW --> https://edstockapi-46617bdcc216.herokuapp.com/backtest/

## Introduction
This backend sytem fetches stock data from Alpha Vantage API, implements a basic backtesting module, integrates a pre-trained machine learning model for price predictions, and generates reports that compare historical prices to a prediction based on a linear regression model. 

## Technologies Used
- Django
- PostgreSQL (AWS RDS)
- Docker
- GitHub Actions
- Alpha Vantage API
- Matplotlib / Plotly for reporting
- Heroku for deployment

WANT TO TRY THE APP WITHOUT SETTING UP YOUR OWN SYSTEM? GO TO DEPLOYMENT NOW --> https://edstockapi-46617bdcc216.herokuapp.com/backtest/


## Local Setup
1. **Clone the repository**: 
   `git clone <repository-url>`  
   `cd <repository-directory>`
2. **Set up a virtual environment (optional but recommended)**: 
   `python -m venv venv`  
   `source venv/bin/activate`  # On Windows use `venv\Scripts\activate`
3. **Install dependencies**: 
   `pip install -r requirements.txt`
4. **Create a `.env` file in the root directory with the following content**: 
   `DATABASE_URL=your_database_url`  
   `DJANGO_SECRET_KEY=your_secret_key`  
   `ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key`  
   `DEBUG=True`

## Running Migrations and Seeding Data
1. **Apply migrations**: 
   `python manage.py migrate`
2. **Create a superuser (optional)**: 
   `python manage.py createsuperuser`
3. **Run the development server**: 
   `python manage.py runserver`

## Deployment on AWS

### Dockerized Setup
1. **Build the Docker image**: 
   `docker build -t my-django-app .`
2. **Run the Docker container**: 
   `docker run -d -p 8000:8000 my-django-app`

### Using AWS RDS
1. **Create an RDS instance**: 
   - Go to the RDS section in the AWS Management Console.
   - Launch a new PostgreSQL instance, configuring it according to your needs.
2. **Update your `.env` file with the RDS connection details**: 
   `DATABASE_URL=postgres://username:password@your-rds-endpoint:5432/dbname`

### CI/CD Pipeline
1. **Set up GitHub Actions**: 
   - Create a `.github/workflows/deploy.yml` file with the following content:
name: Deploy to AWS

on: push: branches: - main

jobs: deploy: runs-on: ubuntu-latest steps: - name: Checkout code uses: actions/checkout@v2


     - name: Set up Docker Buildx
       uses: docker/setup-buildx-action@v1

     - name: Login to DockerHub
       uses: docker/login-action@v1
       with:
         username: ${{ secrets.DOCKER_USERNAME }}
         password: ${{ secrets.DOCKER_PASSWORD }}

     - name: Build and push Docker image
       uses: docker/build-push-action@v2
       with:
         context: .
         push: true
         tags: your_dockerhub_username/my-django-app:latest

     - name: Deploy to AWS
       run: |
         # Add your deployment commands here, e.g., AWS CLI commands


### Handling Environment Variables
- Use a `.env` file in the root directory to securely store sensitive information.
