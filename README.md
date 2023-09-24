```

# Run locally

source .venv/bin/activate
python3 -m pip install -r app/requirements.txt


uvicorn main:app --reload




# Run in docker:

docker-compose up client data --build

# Run tests:

pytest


# Get sql cli:

docker exec -it ai-budget-bot-data-1 psql -U myuser -W mydatabase


# Reset DB:

docker ps -a --filter volume=ai-budget-bot_pgdata

docker stop [CONTAINT_ID]
docker container rm [CONTAINT_ID]

docker volume rm ai-budget-bot_pgdata
```
