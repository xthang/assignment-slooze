import uvicorn

from src.constants.env import ENVIRONMENT
from src.utils.logging import logger
from src.api.app import app


logger.info(f'--- Running in {ENVIRONMENT} mode')


if __name__ == '__main__':
   uvicorn.run(app)
