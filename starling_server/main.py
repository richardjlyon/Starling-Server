import uvicorn

from starling_server.db.edgedb.database import Database
from starling_server.server.controller import Controller

db = Database()
controller = Controller(db=db)

def run():
    uvicorn.run("starling_server.server.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()