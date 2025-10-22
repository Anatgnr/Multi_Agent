from crewai import Agent

def create_dependency_manager(llm=None, mcp_tool=None):
    return Agent(
        name="DependencyManager",
        role="Gestionnaire de dépendances",
        goal="Lister les bibliothèques Python nécessaires au bon fonctionnement du projet.",
        backstory="Vous êtes un expert en gestion des dépendances et en configuration d'environnements.",
        llm=llm,
        mcp_tool=mcp_tool
    )
