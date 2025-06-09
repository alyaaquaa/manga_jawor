from dotenv import load_dotenv
import os
load_dotenv() 

class Config: SECRET_KEY = os.getenv('SECRET_KEY', 'defaultsecretkey') 

# Używamy pełnego URI do PostgreSQL z Rendera (ustawionego jako zmienna środowiskowa) 
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') 
SQLALCHEMY_TRACK_MODIFICATIONS = False 
 
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME') 
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL') 
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
