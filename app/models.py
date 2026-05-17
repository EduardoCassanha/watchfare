from pydantic import BaseModel

class Flight(BaseModel):
    date: str
    origin: str
    destination: str
    price: float
    duration: int | None = None
    airline: str
    departure: str
    arrival: str

class Combination(BaseModel):
    outbound_date: str
    return_date: str
    outbound: Flight
    inbound: Flight
    total: float

class SearchResult(BaseModel):
    timestamp: str
    combinations: list[Combination]
    best_price: float
    below_target: bool