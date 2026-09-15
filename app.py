import streamlit as st
import asyncio
import json
import re
from agents.sql_agent import sql_agent
from database.connection import run_sql_query

# পেজ কনফিগারেশন
st.set_page_config(page_title="AI Data Analyst", page_icon="🤖", layout="wide")

st.title("🤖 AI Data Analyst")
st.markdown("##### Enterprise-grade Text-to-SQL AI Agent with Session Memory")

# চ্যাট হিস্টোরি স্টেট ইনিশিয়ালাইজ করা
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# আগের চ্যাট মেসেজগুলো স্ক্রিনে রেন্ডার করা
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ইউজারের মেসেজ ইনপুট নেওয়া
if user_prompt := st.chat_input("Ask me about users, sales, or signups (e.g., 'How many users are from Bangladesh?')"):
    
    # ইউজারের মেসেজ স্ক্রিনে দেখানো এবং সেভ করা
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    
    # এআই এজেন্টের রেসপন্স তৈরি করা
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        with st.spinner("Analyzing database and thinking..."):
            try:
                # 🧠 মেমোরি/কনটেক্সট কম্প্রেশন লজিক:
                # আগের চ্যাট হিস্টোরি থেকে শেষ ৩টি মেসেজ নিয়ে কনটেক্সট তৈরি করা (যাতে টোকেন ওভারফ্লো না হয়)
                recent_history = st.session_state.chat_history[-4:-1]
                history_context = ""
                if recent_history:
                    history_context = "Previous Conversation History for Context:\n"
                    for msg in recent_history:
                        history_context += f"{msg['role'].capitalize()}: {msg['content']}\n"
                    history_context += "\n--- End of History ---\n"

                # মূল প্রম্পটের সাথে চ্যাট হিস্টোরি যুক্ত করা
                final_prompt_with_memory = f"{history_context}Current User Question: {user_prompt}"

                # ১. মডেলকে প্রম্পটটি পাঠানো এবং তার প্রথম রেসপন্স নেওয়া
                async def run_agent(prompt):
                    return await sql_agent.run(prompt)
                
                result = asyncio.run(run_agent(final_prompt_with_memory))
                bot_response = result.output 
                
                # ২. টুল কল ইন্টারসেপশন (Tool Call Interception)
                is_tool_call = False
                sql_to_run = None
                
                if isinstance(bot_response, str) and "execute_database_query" in bot_response:
                    is_tool_call = True
                    match = re.search(r'"sql_query"\s*:\s*"([^"]+)"', bot_response)
                    if match:
                        sql_to_run = match.group(1)
                
                # ৩. যদি টুল কল আইডেন্টিফাই হয়, তবে ডাটাবেজে কুয়েরি রান করা
                if is_tool_call and sql_to_run:
                    st.toast(f"Running Generated SQL: {sql_to_run}", icon="⚡")
                    print(f"\n⚡ [Executing Intercepted SQL with Memory Context]: {sql_to_run}")
                    
                    db_result = run_sql_query(sql_to_run)
                    
                    follow_up_prompt = (
                        f"Context: {history_context}\n"
                        f"The user asked: '{user_prompt}'\n"
                        f"The database returned the following result:\n{json.dumps(db_result)}\n\n"
                        f"Please explain this result to the user in natural language based on the context. Do not return JSON."
                    )
                    
                    final_result = asyncio.run(run_agent(follow_up_prompt))
                    bot_response = final_result.output
                
                # স্ক্রিনে ফাইনাল আউটপুট দেখানো
                response_placeholder.markdown(bot_response)
                
                # চ্যাট হিস্টোরিতে সেভ করা
                st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
