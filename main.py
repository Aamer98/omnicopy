from fastapi import FastAPI
from datetime import datetime
from fastapi import HTTPException, Request, Response
from typing import Any
import random

app = FastAPI(root_path='/api/v1')

# This decorator describes how we associate a webpage visit to a certain function.
@app.get("/")
async def root():
    return {"message": "Hello world!"}

data: Any = [
    {
        "campaign_id": 1,
        "name": "Summer Launch",
        "due_date": datetime.now(),
        "created_at": datetime.now()
    },
    {
        "campaign_id": 2,
        "name": "Summer Launch",
        "due_date": datetime.now(),
        "created_at": datetime.now()
    }
]

@app.get("/campaigns")
async def read_campaigns():
    return {"campaigns": data}

@app.get("/campaigns/{id}")
async def read_campaign(id: int):
    for campaign in data:
        if campaign.get("campaign_id") == id:
            return {"campaign": campaign}
    return HTTPException(status_code=404)

@app.post("/campaigns", status_code=201)
async def create_campaign(body: dict[str, Any]):
    # body = await request.json()

    new = {
        "campaign_id": random.randint(100, 1000),
        "name": body.get("name"),
        "due_date": body.get("due_date"),
        "created_at": datetime.now()        
    }

    data.append(new)
    return {"campaign": new}


@app.put("/campaign/{id}")
async def update_campaign(id: int, body: dict[str, Any]):

    for idx, campaign in enumerate(data):
        if campaign.get('campaign_id') == id:

            updated: Any = {
                "campaign_id":id,
                "name": body.get("name"),
                "due_date": body.get("due_date"),
                "created_at": campaign.get("id")
            }

            data[idx] = updated
            return {"campaign": updated}
    raise HTTPException(status_code=404)


@app.delete("/campaign/{id}")
async def delete_campaign(id: int):

    for idx, campaign in enumerate(data):
        if campaign.get('campaign_id') == id:

            data.pop(idx)
            return Response(status_code=204)
        
    raise HTTPException(status_code=404)


"""
Campaigns
- campaign_id
- name
- due_date
- created_at

pieces
- piece_id
- campaign_id
- name
- content
- content_type
- created_at
"""