import sqlite3
import yaml
import streamlit as st
from Auth import Auth

class Sidebar():
	def __init__(self, auth: Auth):
		self.name = auth.get_name()
		self.authentication_status = auth.get_authentication_status()
		self.username = auth.get_username()
		self.authenticator = auth.get_authenticator()
		self.temperature = 0.5

	def get_temperature(self):
		return self.temperature
	
	def set_temperature(self, temperature):
		self.temperature = temperature
	
	# FUNCTION: START A NEW CHAT
	def new_chat(self):
		"""
		Clears session state and starts a new chat.
		"""
		if st.session_state["responses"]:
			save = []
			for i in range(len(st.session_state["responses"]) - 1, -1, -1):
				save.append("User:" + str(st.session_state["prompts"][i]))
				save.append("Bot:" + str(st.session_state["responses"][i]))
			st.session_state["stored_sessions"].append(save)
			conn = sqlite3.connect('data.db', check_same_thread=False)
			c = conn.cursor()
			c.execute("""INSERT INTO stored_sessions VALUES (?, ?)""", (self.username, str(save)))
			c.execute("""DELETE FROM responses WHERE username = ?""", (self.username,))
			c.execute("""DELETE FROM prompts WHERE username = ?""", (self.username,))
			conn.commit()
			conn.close()
			st.session_state["responses"] = []
			st.session_state["prompts"] = []
        

	# FUNCTION: CLEAR CHAT HISTORY
	def clear_history(self):
		conn = sqlite3.connect('data.db', check_same_thread=False)
		c = conn.cursor()
		c.execute("""DELETE FROM stored_sessions WHERE username = ?""", (self.username,))
		c.execute("""DELETE FROM responses WHERE username = ?""", (self.username,))
		c.execute("""DELETE FROM prompts WHERE username = ?""", (self.username,))
		conn.commit()
		conn.close()
		del st.session_state.stored_sessions
		del st.session_state.responses
		del st.session_state.prompts


	def main(self):
		# SIDEBAR: AUTH CHECK
		if self.authentication_status is False:
			st.sidebar.error('Username/password is incorrect')
		elif self.authentication_status is None:
			st.sidebar.warning('Please enter your username and password')
			st.warning('👈 Please Use Sidebar To Login/Register To Use Natural Law')


		# SIDEBAR: REGISTER & FORGOT FORMS
		st.sidebar.text(" ")
		st.sidebar.text(" ")
		if self.authentication_status is False or self.authentication_status is None:
			# REGISTER USER
			with st.sidebar.expander("📝 Register", expanded=False):
				try:
					if self.authenticator.register_user('Register user', preauthorization=False):
						st.success('User registered successfully')
						with open('config.yaml', 'w') as file:
							yaml.dump(self.config, file, default_flow_style=False)
				except Exception as e:
					st.error(e)
			with st.sidebar.expander("🤷‍♂️ Forgot Password/Username", expanded=False):
				# FORGOT PASSWORD
				try:
					username_forgot_pw, email_forgot_password, random_password = self.authenticator.forgot_password('Forgot password')
					if username_forgot_pw:
						st.success('New Temporary Password: ' + random_password)
						with open('config.yaml', 'w') as file:
							yaml.dump(self.config, file, default_flow_style=False)
					else:
						st.error('Username not found')
				except Exception as e:
					st.error(e)
				# FORGOT USERNAME
				try:
					username_forgot_username, email_forgot_username = self.authenticator.forgot_username('Forgot username')
					if username_forgot_username:
						st.success('Username: ' + username_forgot_username)
						with open('config.yaml', 'w') as file:
							yaml.dump(self.config, file, default_flow_style=False)
					else:
						st.error('Email not found')
				except Exception as e:
					st.error(e)

		# SIDEBAR: APP INFO
		if self.authentication_status:
			st.sidebar.header("Welcome " + self.name + "! 👋")
			st.sidebar.markdown(""":black[Use Natural Law to help you think!]""")
			with st.sidebar.expander("✍️ Prompt Examples", expanded=False):
				st.markdown(
				""" 
					:black[For Best Results, Use A Similar Format To:\n]
					------
					:black[1. *"How does an AI understand the concept of consciousness?"*]
					:black[2. *"What is your perspective on the meaning of life?"*]
					:black[3. *"Can AI truly experience emotions, or is it just simulating them based on programmed responses?"*]
					"""
				)
			st.sidebar.progress(100)



		# SIDEBAR: CHAT HISTORY
		if self.authentication_status:
			st.sidebar.header("Chat History")
			st.sidebar.button("New Chat", on_click=self.new_chat, type="primary")
			if st.session_state.stored_sessions:
				st.sidebar.button("Clear History", on_click=self.clear_history, type="secondary")
			st.sidebar.text(" ")

			# SIDEBAR: DISPLAY STORED SESSIONS
			if st.session_state.stored_sessions:
				for i in range(len(st.session_state.stored_sessions) - 1, -1, -1):
					with st.sidebar.expander(label=f"Conversation {i+1}", expanded=False):
						st.write(st.session_state.stored_sessions[i])
			st.sidebar.text(" ")
			st.sidebar.progress(100)


		# SIDEBAR: SETTINGS, ACCOUNT SETTINGS
		if self.authentication_status:
			st.sidebar.header("Settings")
			with st.sidebar.expander("🧠 Model Settings ", expanded=False):
				temp = st.slider("Randomness", min_value=0.0, max_value=1.0, step=0.01, value=0.5, format='%f',)
				self.set_temperature(temp)
			with st.sidebar.expander("🛠️ Account Settings", expanded=False):
				try:
					if self.authenticator.update_user_details(self.username, 'Update user details'):
						st.success('Entries updated successfully')
						with open('config.yaml', 'w') as file:
							yaml.dump(self.config, file, default_flow_style=False)
				except Exception as e:
					st.error(e)
				try:
					if self.authenticator.reset_password(self.username, 'Reset password'):
						st.success('Password modified successfully')
						with open('config.yaml', 'w') as file:
							yaml.dump(self.config, file, default_flow_style=False)
				except Exception as e:
					st.error(e)
			st.sidebar.text(" ")
			st.sidebar.progress(100)
			
		# SIDEBAR: ACCOUNT SETTINGS & LOGOUT
		if self.authentication_status:
			st.sidebar.text(" ")
			self.authenticator.logout('✌️ Logout', 'sidebar')
			