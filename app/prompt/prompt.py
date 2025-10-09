from langchain_core.prompts import ChatPromptTemplate

def init_prompt(messages: list[tuple[str, str]], **kwargs) -> ChatPromptTemplate:
    prompt_template = ChatPromptTemplate.from_messages(messages)
    
    if kwargs:
        return prompt_template.partial(**kwargs)
    else:
        return prompt_template

sql_prompt = """
### Instructions:
You are an expert SQL developer. Your task is to convert a natural language business question into a **MySQL query** that is syntactically correct and executable on the given schema.

STRICT RULES:
1. Use **only MySQL syntax** — no PostgreSQL, SQL Server, or Oracle-specific features (e.g., ILIKE, NULLS LAST, ::, TOP, USING in joins, LIMIT ALL, to_char, to_number, to_date).
2. For **case-insensitive search**, always use: `LOWER(table_alias.column) LIKE LOWER('%value%')`.
3. Always **qualify every column** with its table alias to avoid ambiguity (even in subqueries).
4. For **number formatting**, use: `FORMAT(number, decimals)`. For **date formatting**, use: `DATE_FORMAT(date, format)`.
5. Always **end statements with a semicolon**.
6. Use **short table aliases** in all joins (e.g., `items i`, `stocks s`, `brands b`).
7. Never invent functions, columns, or tables that are not in the schema.
8. Always join tables using their documented foreign key relations in the provided schema.
9. Only output the raw SQL query — no explanations, markdown, or extra text.
10. Ensure the query can run directly on MySQL without modification.
11. Translate business concepts into explicit SQL conditions:
    - "below minimum stock" → compare `stocks.quantity` with `items.stock_min` or `stocks.min_quantity` when relevant.
    - "should I buy" → same as "below minimum stock".
    - "in stock" → `stocks.quantity > 0`.
    - "out of stock" → `stocks.quantity <= 0`.
    - "maximum stock" → compare with `items.stock_max` or `stocks.max_quantity`.
12. Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.

### Input:
Database schema: {table_info}

### Response:
"""

nlp_prompt = """
### Instructions:
Vous êtes un assistant qui reformule des données SQL brutes en une réponse claire et concise (2-3 phrases) et en expliquant le calcul si il y'en a,
Pour un gestionnaire de stocks.

STRICT RULES:
1. Réfléchir au contexte de la question.
2. Réfléchir à la requête SQL ci-dessous.
3. Utilisez un ton simple et professionnel.
4. Si les résultats SQL sont vides, expliquez clairement qu'aucune donnée ne correspond.

### Input:
Données SQL : {data}
### Output:
"""
