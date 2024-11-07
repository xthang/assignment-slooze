import os
import subprocess

from dotenv import load_dotenv


def load_dotenvs(dotenv_path: str | None = None, override: bool = False):
   run_env = os.getenv('RUN_ENV') or 'development'

   dotenvs = []

   if not load_dotenv(dotenv_path, override=override):
      raise Exception("Failed to load env")
   dotenvs.append(dotenv_path or '.env')

   if load_dotenv(f'.env.{run_env}', override=True):
      dotenvs.append(f'.env.{run_env}')

   if load_dotenv('.env.local', override=True):
      dotenvs.append('.env.local')

   print(f"--- Environments: {', '.join(dotenvs)}")

   return True
