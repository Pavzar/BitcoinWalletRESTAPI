# Simple Bitcoin Wallet API

## Description:
A basic REST API that simulates a Bitcoin wallet, allowing users to:

* Add new unspent transaction entries
* List all transactions
* Get the current balance (BTC and EUR)
* Create transfers from existing unspent transactions

## Prerequisites

* Python 3.10 or newer (https://www.python.org/downloads/)
* pip (Python package manager, usually included with Python installation)

## Installation

1. Clone the repository:

   - git clone https://github.com/Pavzar/BitcoinWalletRESTAPI

2. Navigate to the project directory:

   - cd BitcoinWalletRESTAPI
   
3. Create a virtual environment (recommended):

   - Linux/macOS: python3 -m venv env
   - Windows: python -m venv env
   
4. Activate the virtual environment:

   - Linux/macOS: source env/bin/activate
   - Windows: env\Scripts\activate.bat
   
5. Install dependencies:

   - pip install -r requirements.txt 
  

## Running the Application

- Ensure you have an SQLite database file named transactions.db in the project's root directory. If you don't have one, it will be automatically created when you first run the application.

 ### Start the FastAPI development server:

 - uvicorn main:app --reload

### Accessing the API

The API will be running at: http://127.0.0.1:8000

### API Documentation (with Swagger UI)

Automatically generated documentation will be available at: http://127.0.0.1:8000/docs

### Endpoints

- /transactions (GET): Lists all transactions.
- /transactions (POST): Adds a new unspent transaction by default (or you can set to spent: true to add spent transaction).
- /balance (GET): Gets the current wallet balance.
- /transfer (POST): Initiates a transfer.
