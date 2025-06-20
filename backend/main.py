from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from datetime import datetime, timedelta
from typing import Dict

app = FastAPI(title="ContentGen API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Simple in-memory rate limiting (per IP)
RATE_LIMIT = 5  # free users get 5 requests per day
request_counts: Dict[str, Dict[str, int]] = {}


def check_rate_limit(ip: str):
    today = datetime.utcnow().date().isoformat()
    counts = request_counts.setdefault(ip, {})
    if counts.get("date") != today:
        counts["date"] = today
        counts["count"] = 0
    if counts["count"] >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Daily limit reached")
    counts["count"] += 1


class DescriptionRequest(BaseModel):
    product_name: str


@app.post("/generate-description")
async def generate_description(data: DescriptionRequest, request: Request):
    check_rate_limit(request.client.host)
    prompt = f"Write a compelling product description for this product: '{data.product_name}' in two sentences."
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return {"result": completion.choices[0].message["content"].strip()}


class BlogRequest(BaseModel):
    keyword: str
    length: int = 500


@app.post("/generate-blog")
async def generate_blog(data: BlogRequest, request: Request):
    check_rate_limit(request.client.host)
    prompt = (
        f"Write a blog post about '{data.keyword}' with approximately {data.length} characters."
    )
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return {"result": completion.choices[0].message["content"].strip()}


class TagRequest(BaseModel):
    keyword: str


@app.post("/generate-tags")
async def generate_tags(data: TagRequest, request: Request):
    check_rate_limit(request.client.host)
    prompt = f"Suggest relevant social media hashtags for '{data.keyword}'."
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return {"result": completion.choices[0].message["content"].strip()}


class TranslateRequest(BaseModel):
    text: str
    target_language: str


@app.post("/translate")
async def translate(data: TranslateRequest, request: Request):
    check_rate_limit(request.client.host)
    prompt = (
        f"Translate the following text into {data.target_language}:\n{data.text}"
    )
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return {"result": completion.choices[0].message["content"].strip()}


@app.get("/")
async def root():
    return {"message": "ContentGen API"}

