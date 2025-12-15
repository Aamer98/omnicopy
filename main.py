from fastapi import FastAPI
from datetime import datetime, timezone
from fastapi import HTTPException, Depends
from typing import Any
import random
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, create_engine, Field, select
from typing import Annotated, Generic, TypeVar
from contextlib import asynccontextmanager

 # Custom Type
class Campaign(SQLModel, table=True):
    campaign_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    due_date: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=True, index=True)

class CampaignCreate(SQLModel):
    name: str 
    due_date: datetime | None = None

# Define SQLite Database connection
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# engine creation
# check_same_thread=False is required for SQLite when:
# FastAPI uses multiple threads
# or async request handling
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args = connect_args)

# create table
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Database session dependency
def get_session():
    # context manager
    # begin transaction, do work, commit close session
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# Used when opening or closing api
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Campaign)).first():
            session.add_all([
                Campaign(name="Summer Launch", due_date=datetime.now()),
                Campaign(name="Black Friday", due_date=datetime.now())])
            session.commit()
    yield

app = FastAPI(root_path='/api/v1', lifespan=lifespan)

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    data: T


@app.get("/campaigns", response_model=Response[list[Campaign]])
async def read_campaigns(session: SessionDep):
    data = session.exec(select(Campaign)).all()
    return {"data": data}


@app.get("/campaigns/{id}", response_model=Response[Campaign])
async def read_campaign(id: int, session: SessionDep):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404)
    return {"data": data}


@app.post("/campaigns", status_code=201, response_model=Response[Campaign])
async def create_campaign(campaign: CampaignCreate, session: SessionDep):
    db_campaign = Campaign.validate(campaign)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign) # makes sure that the campaign has the most upto date data
    return {"data": db_campaign}


@app.put("/campaigns/{id}", response_model=Response[Campaign])
async def update_campaign(id: int, campaign:CampaignCreate, session:SessionDep):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404)
    data.name = campaign.name
    data.due_date = campaign.due_date
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data": data}


@app.delete("/campaigns/{id}", status_code=204)
async def delete_campaign(id: int, session: SessionDep):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404)
    session.delete(data)
    session.commit()
    return None

# @app.put("/campaign/{id}")
# async def update_campaign(id: int, body: dict[str, Any]):

#     for idx, campaign in enumerate(data):
#         if campaign.get('campaign_id') == id:

#             updated: Any = {
#                 "campaign_id":id,
#                 "name": body.get("name"),
#                 "due_date": body.get("due_date"),
#                 "created_at": campaign.get("id")
#             }

#             data[idx] = updated
#             return {"campaign": updated}
#     raise HTTPException(status_code=404)


# @app.delete("/campaign/{id}")
# async def delete_campaign(id: int):

#     for idx, campaign in enumerate(data):
#         if campaign.get('campaign_id') == id:

#             data.pop(idx)
#             return Response(status_code=204)
        
#     raise HTTPException(status_code=404)


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