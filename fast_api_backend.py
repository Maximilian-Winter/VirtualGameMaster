import dataclasses

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List
import json
import asyncio
from contextlib import asynccontextmanager

from virtual_game_master import VirtualGameMasterConfig, VirtualGameMaster
from chat_api_selector import VirtualGameMasterChatAPISelector


@dataclasses.dataclass
class State:
    rpg_app: VirtualGameMaster


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    config = VirtualGameMasterConfig()
    # config.GAME_SAVE_FOLDER = "chat_history/new_game"
    api_selector = VirtualGameMasterChatAPISelector(config)
    api = api_selector.get_api()
    app.state = State(rpg_app=VirtualGameMaster(config, api))
    app.state.rpg_app.load()
    yield
    # Shutdown
    # Add any cleanup code here if needed


app = FastAPI(lifespan=lifespan)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class Message(BaseModel):
    content: str


class EditMessage(BaseModel):
    id: int
    content: str


class TemplateFields(BaseModel):
    fields: Dict[str, str]


@app.post("/api/send_message")
async def send_message(message: Message):
    response_generator, should_exit = app.state.rpg_app.process_input(message.content, stream=True)
    response = "".join(list(response_generator))
    return {"response": response, "should_exit": should_exit}


@app.post("/api/edit_message")
async def edit_message(edit_message: EditMessage):
    success = app.state.rpg_app.edit_message(edit_message.id, edit_message.content)
    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=404, detail="Message not found")


@app.get("/api/get_template_fields")
async def get_template_fields():
    return {"fields": app.state.rpg_app.template_fields}


@app.post("/api/update_template_fields")
async def update_template_fields(fields: TemplateFields):
    app.state.rpg_app.template_fields.update(fields.fields)
    app.state.rpg_app.save()
    return {"status": "success"}


@app.post("/api/save_game")
async def save_game():
    app.state.rpg_app.manual_save()
    return {"status": "success"}


@app.get("/api/get_chat_history")
async def get_chat_history():
    return {"history": app.state.rpg_app.history.to_list()}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            response_generator, should_exit = app.state.rpg_app.process_input(message['content'], stream=True)

            async for chunk in async_generator(response_generator):
                await websocket.send_text(json.dumps({"type": "chunk", "content": chunk}))
                await asyncio.sleep(0)  # Allow other tasks to run

            await websocket.send_text(json.dumps({"type": "end", "should_exit": should_exit}))

            if should_exit:
                break
    except WebSocketDisconnect:
        print("WebSocket disconnected")


async def async_generator(sync_generator):
    for item in sync_generator:
        yield item
        await asyncio.sleep(0)  # Allow other tasks to run


# Mount the static files after all other routes
# app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
