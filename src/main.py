import asyncio

from uvicorn import Config, Server

from api.app import app


def start_server():
    config = Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        forwarded_allow_ips=["*"],
    )
    server = Server(config)
    return server.serve()


def main():
    loop = asyncio.new_event_loop()
    loop.create_task(start_server())
    loop.run_forever()


if __name__ == "__main__":
    main()
