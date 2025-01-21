from crewai import Agent

def create_story_points_agent():
    return Agent(
        role="Analista de Story Points",
        goal="Somar os valores de story points agrupados por dia ou semana.",
        backstory="Você é um especialista em métricas ágeis e soma story points para análise de progresso.",
        verbose=True
    )