# YAFA (yet-another-finance-app)

## More documentation soon

### How to Run

#### Expected File Structure:
```
YAFA\
    data\ (CREATE PRIOR TO RUNNING)
        yafaDB.db
    yafa\
    .gitignore
    .env(.template)
    docker-compose.yaml
    Dockerfile
    README.md
    requirements.txt
```

See .env.template for how to create ".env" file required.
Ensure the local/persistent data directory exists prior to running.

### Steps
```
git clone https://github.com/nickclason/YAFA.git
cd YAFA
mkdir data

# Ensure .env is properly configured and docker-compose volume is set up if using compose.

Run via included docker-compose.yaml: docker compose up --build
Run via command line using python: python yafa/app/main.py (requires dependencies see requirements.txt)
```



