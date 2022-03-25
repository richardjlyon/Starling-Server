# import uvicorn
#
# from starling_server.db.edgedb.database import Database
# from starling_server.server.account_listener import setup_account_listener
# from starling_server.server.log_listener import setup_log_listener
#
# db = Database()
#
#
# # dispatcher = RouteDispatcher(database=db)
#
#
# def run():
#     setup_log_listener()
#     setup_account_listener()
#
#     uvicorn.run(
#         "starling_server.server.app:app", host="0.0.0.0", port=8000, reload=True
#     )
#
#
# if __name__ == "__main__":
#     run()
