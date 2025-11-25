import sqlite3
from mitmproxy import http, ctx

DB_FILE = "logs.db"

def create_table():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_url TEXT,
            request_method TEXT,
            request_headers TEXT,
            request_body TEXT,
            response_status_code INTEGER,
            response_headers TEXT,
            response_body TEXT
        )
    """)
    conn.commit()
    conn.close()

def load(loader):
    create_table()
    ctx.log.info("Proxy loaded and database table created.")

class GeminiLogger:
    def request(self, flow: http.HTTPFlow) -> None:
        if "generativelanguage.googleapis.com" in flow.request.host:
            ctx.log.info(f"Request: {flow.request.method} {flow.request.url}")

    def response(self, flow: http.HTTPFlow) -> None:
        if "generativelanguage.googleapis.com" in flow.request.host:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            request = flow.request
            response = flow.response

            cursor.execute(
                """
                INSERT INTO logs (
                    request_url, request_method, request_headers, request_body,
                    response_status_code, response_headers, response_body
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request.url,
                    request.method,
                    str(request.headers),
                    request.get_text(),
                    response.status_code,
                    str(response.headers),
                    response.get_text(),
                ),
            )

            conn.commit()
            conn.close()
            ctx.log.info(f"Logged request to {request.url} in the database.")

addons = [GeminiLogger()]
