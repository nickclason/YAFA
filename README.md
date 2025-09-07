# YAFA (Yet Another Finance App)

⚠️ This README has been refined by AI. I have vetted the output lightly and believe it to be mostly accurate. Take that for what you will ⚠️

YAFA is a personal finance tool that helps you aggregate and view your financial data.  
It is designed to work with **[SimpleFIN](https://simplefin.org/)**, a standard protocol that allows financial institutions to share account data securely.  

## Current functionality: Pull all account/transaction data from SimpleFIN and store in a local sqlite db

## What is SimpleFIN?

[SimpleFIN](https://simplefin.org/) is an open protocol for connecting financial institutions with applications like YAFA.  
It was created with **privacy and simplicity** in mind:

- ✅ **You control your data** – YAFA never stores or shares credentials beyond what is necessary to connect via SimpleFIN.  
- 🔒 **Security first** – credentials are exchanged securely, and only for the accounts you choose to link.  
- 📊 **Read-only access** – SimpleFIN provides access to account balances and transactions, not the ability to move money.  
- 🛠️ **Transparency** – SimpleFIN is open-source (??? Is it? IDK this is certainly AI Generated) and well-documented.  

In short, SimpleFIN is alternative to services like Plaid (using the [MX platform](https://www.mx.com/) to connect)
---

## Running YAFA

### Prerequisites

- Docker (recommended) **or** Python 3.11+
- `.env` file created from `.env.template`
- Local `data/` directory for persistent storage

### Expected Project Structure
```
YAFA/
├── data/ # CREATE THIS DIRECTORY BEFORE RUNNING
├── yafa/
├── .gitignore
├── .env (.env.template provided)
├── docker-compose.yaml
├── Dockerfile
├── README.md
└── requirements.t
```


---

### Run with Docker (Recommended)
```
docker compose up --build
```

### Run with Python (Recommended using venv/uv/etc. or some sort of package manager)
```
pip install -r requirements.txt
python yafa/app/main.py
```