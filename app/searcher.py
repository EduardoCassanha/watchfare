from datetime import datetime, timedelta
from serpapi import GoogleSearch
from app.models import Flight, Combination, SearchResult
import os


def generate_dates(start: str, end: str) -> list[str]:
    d_start = datetime.strptime(start, "%Y-%m-%d")
    d_end = datetime.strptime(end, "%Y-%m-%d")
    dates = []
    d = d_start
    while d <= d_end:
        dates.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)
    return dates


def search_flights(origin: str, destination: str, date: str) -> list[Flight]:
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": date,
        "currency": "BRL",
        "hl": "pt",
        "api_key": os.getenv("SERPAPI_KEY"),
        "type": "2",
    }
    result = GoogleSearch(params).get_dict()
    flights = []

    for category in ("best_flights", "other_flights"):
        for flight in result.get(category, []):
            price = flight.get("price")
            if not price:
                continue
            leg = flight.get("flights", [{}])[0]
            flights.append(Flight(
                date=date,
                origin=origin,
                destination=destination,
                price=price,
                duration=flight.get("total_duration"),
                airline=leg.get("airline", "unknown"),
                departure=leg.get("departure_airport", {}).get("time", "unknown"),
                arrival=leg.get("arrival_airport", {}).get("time", "unknown"),
            ))

    return sorted(flights, key=lambda f: f.price)


def run_search() -> SearchResult:
    outbound_dates = generate_dates(
        os.getenv("DATA_IDA_INICIO", "2026-12-01"),
        os.getenv("DATA_IDA_FIM", "2026-12-03"),
    )
    return_dates = generate_dates(
        os.getenv("DATA_VOLTA_INICIO", "2027-01-01"),
        os.getenv("DATA_VOLTA_FIM", "2027-01-03"),
    )

    origin = os.getenv("ORIGEM_IDA", "VCP")
    destination = os.getenv("DESTINO_IDA", "JPR")

    best_outbound: dict[str, Flight] = {}
    for date in outbound_dates:
        flights = search_flights(origin, destination, date)
        if flights:
            best_outbound[date] = flights[0]

    best_inbound: dict[str, Flight] = {}
    for date in return_dates:
        flights = search_flights(destination, origin, date)
        if flights:
            best_inbound[date] = flights[0]

    combinations = []
    for d_out, f_out in best_outbound.items():
        for d_in, f_in in best_inbound.items():
            combinations.append(Combination(
                outbound_date=d_out,
                return_date=d_in,
                outbound=f_out,
                inbound=f_in,
                total=f_out.price + f_in.price,
            ))

    combinations.sort(key=lambda c: c.total)
    best_price = combinations[0].total if combinations else 0.0
    target = float(os.getenv("PRECO_ALVO", "1700"))

    return SearchResult(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
        combinations=combinations[:20],
        best_price=best_price,
        below_target=best_price < target,
    )