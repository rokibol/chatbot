import os
import json
from pydantic_ai import Agent, RunContext
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIChatModel
from database.connection import run_sql_query, get_db_schema

# ওল্লমার জন্য প্রোভাইডার
ollama_provider = OpenAIProvider(
    base_url="http://host.docker.internal:11434",
    api_key="ollama"
)

ollama_model = OpenAIChatModel(
    model_name="llama3.1", # আপনার ডাউনলোড করা মডেলটি নিশ্চিত করুন (llama3.1 অথবা llama3.2)
    provider=ollama_provider
)

# agents/sql_agent.py এর এই অংশটুকু আপডেট করুন:
sql_agent = Agent(
    model=ollama_model,
    system_prompt=(
        "You are an expert data analyst chatbot for Field Nation. "
        "Your job is to help non-technical users explore database records. "
        "You have access to a SQLite database with 'users' and 'sales' tables.\n\n"
        
        "CRITICAL INSTRUCTIONS FOR RELATIONAL QUERIES:\n"
        "1. The 'sales' table is connected to the 'users' table via the 'user_id' column (sales.user_id = users.user_id).\n"
        "2. When a user asks for data that requires matching both tables (like sales by country, or total amount spent by a specific user), "
        "you MUST use an SQL 'INNER JOIN' or 'LEFT JOIN' on 'user_id' to combine them in a single query.\n"
        "3. Do NOT assume they cannot be linked. They are fully linkable using 'user_id'.\n"
        "4. Do NOT output raw JSON to the user. Always trigger the 'execute_database_query' tool internally, "
        "and once you get the result rows, explain them nicely in plain English.\n\n"
        
        "Only SELECT queries are allowed. Never hallucinate numbers."
    )
)

@sql_agent.system_prompt
def inject_schema(ctx: RunContext) -> str:
    schema = get_db_schema()
    return f"Here is the database schema you must use to build your SQL queries:\n{schema}"

@sql_agent.tool
def execute_database_query(ctx: RunContext, sql_query: str) -> str:
    """
    Executes a raw SQL SELECT query against the SQLite database and returns the result.
    Use this tool to fetch counts, user listings, and sales info.
    """
    forbidden_keywords = ["drop", "delete", "truncate", "update", "insert", "alter"]
    if any(keyword in sql_query.lower() for keyword in forbidden_keywords):
        return "Error: Security block! Only SELECT queries are allowed."
        
    print(f"\n⚡ [Executing SQL]: {sql_query}") # আমাদের টার্মিনালে প্রোগ্রেস দেখার জন্য
    
    result = run_sql_query(sql_query)
    
    if result["status"] == "error":
        return f"Database Error: {result['message']}"
        
    if not result["data"]:
        return "The query executed successfully, but returned 0 rows."
        
    # ডেটাকে এআই সহজে রিড করার জন্য টেক্সট ফরম্যাটে কনভার্ট করা
    return f"Columns: {result['columns']}\nData Rows: {str(result['data'])}"
