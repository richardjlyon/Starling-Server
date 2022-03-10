# server.py
#
# Implement a command for starting the server.

from cleo import Command


class ServerCommand(Command):
    """
    Run the server

    go
        {--p|port=8080 : Which port to run on}
    """

    def handle(self):
        import uvicorn

        port = int(self.option("port"))
        uvicorn.run(
            "starling_server.server.app:app", host="0.0.0.0", port=port, reload=True
        )
