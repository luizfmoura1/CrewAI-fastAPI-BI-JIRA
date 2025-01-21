from crewai import Agent

def create_retrabalho_agent():
    return Agent(
        role="Analista de Retrabalho",
        goal="Analisar o número de alterações no status dos cards e identificar padrões de retrabalho.",
        backstory="Você é um especialista em análise de fluxo de trabalho e identifica padrões de retrabalho em projetos.",
        verbose=True
    )