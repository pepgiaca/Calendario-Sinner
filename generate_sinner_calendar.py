#!/usr/bin/env python3
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import html

PLAYER_ID = 206570  # Jannik Sinner on SofaScore
CAL_NAME = "Jannik Sinner - Partite"
OUT = Path("docs/sinner.ics")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (calendar generator)",
    "Accept": "application/json",
}

def esc(s: str) -> str:
    s = str(s or "")
    return s.replace("\\", "\\\\").replace(";", r"\;").replace(",", r"\,").replace("\n", r"\n")

def fold(line: str) -> str:
    # RFC5545 line folding at ~75 bytes
    out = []
    while len(line.encode("utf-8")) > 75:
        cut = 75
        while len(line[:cut].encode("utf-8")) > 75:
            cut -= 1
        out.append(line[:cut])
        line = " " + line[cut:]
    out.append(line)
    return "\r\n".join(out)

def dtstamp(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def get_events(kind: str):
    url = f"https://www.sofascore.com/api/v1/player/{PLAYER_ID}/events/{kind}"

    r = requests.get(url, headers=HEADERS, timeout=30)

    print("STATUS:", r.status_code)

    r.raise_for_status()

    data = r.json()

    if isinstance(data, dict):
        return data.get("events", [])

    return []

def main():
    events = []
    try:
        events += get_events("next")
    except Exception as e:
        print("Errore caricamento prossime partite:", e)

    # Opzionale: include anche le ultime partite già giocate, così nel calendario resta uno storico recente.
    try:
        events += get_events("last")
    except Exception as e:
        print("Errore caricamento ultime partite:", e)

    seen = set()
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Giuseppe//Sinner Calendar//IT",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{esc(CAL_NAME)}",
        "X-WR-TIMEZONE:Europe/Rome",
        "REFRESH-INTERVAL;VALUE=DURATION:PT1H",
        "X-PUBLISHED-TTL:PT1H",
    ]

    for ev in sorted(events, key=lambda x: x.get("startTimestamp", 0)):
        eid = ev.get("id")
        if not eid or eid in seen or not ev.get("startTimestamp"):
            continue
        seen.add(eid)

        home = ev.get("homeTeam", {}).get("name", "")
        away = ev.get("awayTeam", {}).get("name", "")
        tournament = ev.get("tournament", {}).get("name", "")
        category = ev.get("tournament", {}).get("category", {}).get("name", "")
        round_info = ev.get("roundInfo", {}).get("name") or ev.get("roundInfo", {}).get("round") or ""
        status = ev.get("status", {}).get("description", "")
        ts = int(ev["startTimestamp"])
        start = dtstamp(ts)
        end = dtstamp(ts + 2*60*60)  # durata stimata 2 ore, Apple la aggiornerà al prossimo refresh

        title = f"Sinner: {home} - {away}".strip()
        desc_parts = [
            f"Torneo: {tournament}",
            f"Categoria: {category}",
            f"Turno: {round_info}",
            f"Stato: {status}",
            "Orario e avversario possono cambiare: il feed viene rigenerato automaticamente.",
            f"Fonte: SofaScore player {PLAYER_ID}",
        ]
        desc = "\\n".join([p for p in desc_parts if p and not p.endswith(": ")])

        uid = hashlib.sha1(f"sofascore-{eid}".encode()).hexdigest() + "@sinner-calendar"
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{start}",
            f"DTEND:{end}",
            f"SUMMARY:{esc(title)}",
            f"DESCRIPTION:{esc(desc)}",
            f"LOCATION:{esc(tournament)}",
            f"URL:https://www.sofascore.com/tennis/player/sinner-jannik/{PLAYER_ID}",
            "END:VEVENT",
        ]

    lines.append("END:VCALENDAR")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\r\n".join(fold(x) for x in lines) + "\r\n", encoding="utf-8")
    print(f"Creato {OUT} con {len(seen)} eventi")

if __name__ == "__main__":
    main()
