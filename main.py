# IMPORTS
import os
import sqlite3
import time
import streamlit as st
from langchain import OpenAI
from streamlit_chat import message
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from Auth import Auth
from Sidebar import Sidebar

# SETUP: PAGE CONFIGURATION
st.set_page_config(page_title="Natural Law", page_icon="assets/natural-law.png", layout="centered", initial_sidebar_state="auto") 
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# AUTHENTICATION SETUP
auth = Auth()


# DATABASE SETUP
conn = sqlite3.connect('data.db', check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS responses(username, response)""")
c.execute("""CREATE TABLE IF NOT EXISTS prompts(username, prompt)""")
c.execute("""CREATE TABLE IF NOT EXISTS stored_sessions(username, sessions)""")
conn.commit()


# SETUP: INITIALIZE SESSION STATES
if auth.authentication_status:
    if "responses" not in st.session_state:
        st.session_state["responses"] = c.execute("""SELECT response FROM responses WHERE username = ?""", (auth.username,)).fetchall()
    if "prompts" not in st.session_state:
        st.session_state["prompts"] = c.execute("""SELECT prompt FROM prompts WHERE username = ?""", (auth.username,)).fetchall()
    if "stored_sessions" not in st.session_state:
        st.session_state["stored_sessions"] = c.execute("""SELECT sessions FROM stored_sessions WHERE username = ?""", (auth.username,)).fetchall()
    if "disableWarning" not in st.session_state:
        st.session_state["disableWarning"] = False
    conn.close()


# RUN NATURAL LAW
def natural_law(prompt):
	return "This would be Natural Law's response."



# MAIN APP FUNCTIONALITY
def main():

	# APP LAYOUT
	st.image("assets/natural-law.png", width=150)
	st.title("Natural Law: Your AI Philosopher 🧠")
	status_bar = st.text(" ")
	st.markdown(
		""" 
			> :black[**Hey There, I'm Natural Law 👋**]
			> :black[*🧠 I'm your personal intelligent philosopher, trained on the brightest philosophical minds of the past.*]
			> :black[*🤔 Ask for my stance on something or anything related to the history of philosophy and I will assist!*]
			"""
	)
	st.text("---")


	# SIDEBAR
	sidebar = Sidebar(auth)
	sidebar.main()
        
	# MAIN: RUN NATURAL LAW
	def run_model(specific_prompt: str = None):
		if text_input == "" and specific_prompt is None:
			st.session_state["disableWarning"] = True
			return
		st.session_state["disableWarning"] = False
		# retrieve input
		cur_prompt = specific_prompt if specific_prompt is not None else text_input
		
		# Update status bar
		for i in range(30):
			status_bar.progress(i, text="Sending " + "'" + cur_prompt[0:100] + "'...")
			time.sleep(0.1)
		st.text(" ")

		# Get response
		status_bar.progress(30, text="Executing...")
		response = natural_law({"objective": cur_prompt})

		# Update status bar
		for i in range(30, 100):
			status_bar.progress(i, text="Generating...")
			time.sleep(0.02)
		status_bar.progress(100)

		# Save response
		st.session_state["responses"].append(response)
		st.session_state["prompts"].append(cur_prompt)
		conn = sqlite3.connect('data.db', check_same_thread=False)
		c = conn.cursor()
		c.execute("""INSERT INTO responses VALUES (?, ?)""", (auth.username, str(response)))
		c.execute("""INSERT INTO prompts VALUES (?, ?)""", (auth.username, str(cur_prompt)))
		conn.commit()
		conn.close()


	# SUBMIT BUTTON
	if auth.authentication_status:
		with st.form("submit_user_input", clear_on_submit=True):
			input, submit = st.columns([4, 1])
			text_input = input.text_input(
				"Ask Natural Law Anything:",
				key="input",
				placeholder="Type Here...",
				label_visibility="collapsed",
			)
			submit.form_submit_button(label="Submit", on_click=run_model, type="primary", use_container_width=True)


	# MAIN: DISPLAY EMPTY PROMPT WARNING
	if auth.authentication_status and st.session_state["disableWarning"]:
		st.warning("Please Enter A Prompt")
		st.text(" ")


	# MAIN: DISPLAY CHAT HISTORY
	if auth.authentication_status and st.session_state["responses"]:
		for i in range(len(st.session_state["responses"])-1, -1, -1):
			message(st.session_state["responses"][i], key=str(i))
			message(st.session_state["prompts"][i], is_user=True, key=str(i)+"_user")


if __name__ == "__main__":
	main()