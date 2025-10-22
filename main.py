# main.py
from orchestrator import Orchestrator

if __name__ == "__main__":
    user_prompt = input("💡 Entre ton idée d'application :\n> ")
    orchestrator = Orchestrator()
    orchestrator.run(user_prompt)


# prompt english:
'''
Create a Windows.exe logiciel that captures the input of the user keyboard and mouse and displays it in real-time on the screen. It should also display a counter for each different key pressed and mouse click when the user gives an input. Do a pretty simple UX/UI for this application.
''' 

# prompt french:
'''
Crée un logiciel Windows.exe qui capture en temps réel les entrées clavier et souris de l'utilisateur et les affiche à l'écran. Il doit également afficher un compteur pour chaque touche différente pressée et chaque clic de souris effectué par l'utilisateur. Fais une interface utilisateur simple et agréable pour cette application.
'''