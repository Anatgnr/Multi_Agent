# main.py
from orchestrator import Orchestrator

if __name__ == "__main__":
    user_prompt = input("💡 Entre ton idée d'application :\n> ")
    orchestrator = Orchestrator()
    orchestrator.run(user_prompt)


# prompt:
'''
Create a Windows.exe logiciel that captures the input of the user keyboard and mouse and displays it in real-time on the screen. It should also display a counter for each different key pressed and mouse click when the user gives an input. Do a pretty simple UX/UI for this application.
''' 