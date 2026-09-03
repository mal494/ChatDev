from fastapi import FastAPI
from server.bootstrap import init_app
# pyrefly: ignore [missing-import]
from utils.env_loader import load_dotenv_file

load_dotenv_file()

app = FastAPI(title="DevAll Workflow Server", version="1.0.0")
init_app(app)
