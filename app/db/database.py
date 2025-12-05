import os
import re
import sqlparse
from typing import Optional, Any
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, CursorResult

def create_engine_for_sql_database(connection_string: str) -> Engine:
    username = quote_plus(os.getenv("AI_USERNAME"))
    password = quote_plus(os.getenv("AI_PASSWORD"))
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_DATABASE")
    url = f"{connection_string}//{username}:{password}@{host}:{port}/{database}"
    engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=28800,
        echo=False,
    )
    return engine

def get_element_str(sentence: str, start: str, end: str) -> str:
    sentence_list = sentence.split()
    res = []
    switch: bool = False

    for indexed_sentence in sentence_list:
        if indexed_sentence == start:
            switch = True
        if switch == True:
            res.append(indexed_sentence)
        if indexed_sentence.find(end) != -1:
            switch = False
    return " ".join(res)

def add_limit_select(query: str, max_limit: Optional[int]) -> str:
    if max_limit is None:
        return query.strip().rstrip(';') + ';'
    query = re.sub(r';\s*$', '', query)
    limit_match = re.search(r'\bLIMIT\s+(\d+)', query, re.IGNORECASE)
    if limit_match:
        existing_limit = int(limit_match.group(1))
        if existing_limit > max_limit:
            query = re.sub(
                r'\bLIMIT\s+\d+',
                f'LIMIT {max_limit}',
                query,
                flags=re.IGNORECASE
            )
    else:
        query += f' LIMIT {max_limit}'
    return query.strip() + ';'


def verify_and_extract_sql_query(query: str, max_limit: Optional[int]) -> list[str]:
    query = sqlparse.format(query, reindent=True, keyword_case="upper")
    clean_query = get_element_str(query, "SELECT", ";")
    if not clean_query:
        return []
    queries = clean_query.split(";")
    return [add_limit_select(q.strip(), max_limit) for q in queries if q.strip()]

def extract_content(result: CursorResult) -> list[dict[str, Any]]:
    try:
        rows = result.fetchall()
        if rows:
            return [dict(row._asdict()) for row in rows]
        else:
            return [{"status": "success", "rows_affected": result.rowcount}]
    except Exception:
        return [{"status": "success", "rows_affected": result.rowcount}]

def execute_queries(engine: Engine, query_list: list[str]) -> list[str]:
    results = []

    if not query_list:
        return results
    try:
        with engine.connect() as connection:
            for query in query_list:
                if not query or not query.strip():
                    continue
                clean_query = query.strip().rstrip(';') + ";"
                result = connection.execute(text(clean_query))
                
                extracted_data = extract_content(result)
                results.append(extracted_data)
                
            return results
            
    except Exception as e:
        print(f"Erreur lors de l'exécution des requêtes: {e}")
        raise

def is_empty_result(data: list[str]) -> bool:
    if not isinstance(data, list) or len(data) != 1:
        return False
    row = data[0]
    return isinstance(row, dict) and row.get("rows_affected") == 0