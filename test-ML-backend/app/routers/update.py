from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Literal
import json
import tempfile
from datetime import datetime
from celery import Celery
from celery.result import AsyncResult

 