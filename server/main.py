from typing import Union
from fastapi import FastAPI, HTTPException
import docker
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from docker.errors import DockerException, NotFound

app = FastAPI()

load_dotenv()
# uvicorn main:app --reload --port 3000

class BotBase(BaseModel):
    name: str = "cool_bot"
    owner_id: int
    strategy: str = "supertrend"
    symbol: str = "ETH/USDT"
    description: Union[str, None] = None
    t_frame: str = "1d"
    quantity: float = 120


client = docker.from_env()


@app.get("/")
def read_root():
    return {"Hello": "I am a trading bot server"}


@app.post("/start-container")
def start_bot_container(container_name: str, bot_info: BotBase) -> JSONResponse:
    try:
        # Define environment variables for the container
        environment = {
            "CONTAINER_NAME": container_name,
            "SYMBOL": bot_info.symbol,
            "TIMEFRAME": bot_info.t_frame,
            "LIMIT": "100",
            "AMOUNT_IN_USDT": bot_info.quantity,
        }

        # Define the volume mapping
        volumes = {os.getenv("BOT_SCRIPT_PATH"): {"bind": "/app", "mode": "rw"}}

        # Run the container
        container = client.containers.run(
            "yayin494/trading-bot:tagname",
            command=f"python -u ./{bot_info.strategy}.py",
            name=container_name,
            environment=environment,
            volumes=volumes,
            detach=True,
            mem_limit="128m",
        )

        return JSONResponse(
            content={
                "container_id": container.id,
                "container_name": container_name,
                "status": "running",
            }
        )
    except docker.errors.ContainerError as e:
        # Handle container execution errors
        raise HTTPException(status_code=500, detail=str(e))
    except docker.errors.DockerException as e:
        # Handle other Docker-related errors
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/stop-container")
def stop_bot_container(container_id: str):
    try:
        container = client.containers.get(container_id)
        container.stop()
    except NotFound:
        raise HTTPException(
            status_code=404, detail=f"Container with ID {container_id} not found."
        )
    except DockerException as e:
        print(f"Error stopping docker container {container_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error stopping bot in docker. Please check docker's status: "
            + str(e),
        )
    return {"message": f"Container {container_id} stopped successfully."}


@app.delete("/delete-container")
def delete_bot_container(container_id: str):
    try:
        container = client.containers.get(container_id)
        container.remove()
    except NotFound:
        raise HTTPException(
            status_code=404, detail=f"Container with ID {container_id} not found."
        )
    except DockerException as e:
        print(f"Error deleting docker container {container_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Error deleting bot in docker: " + str(e)
        )
    return {"message": f"Container {container_id} deleted successfully."}
