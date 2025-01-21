from crewai import Agent, Task, Crew

def create_retrabalho_agent():
    rework_agent = Agent(
        role="Analista de Retrabalho",
        goal="Analisar o número de alterações no status dos cards e identificar padrões de retrabalho.",
        backstory="Você é um especialista em análise de fluxo de trabalho e identifica padrões de retrabalho em um board no JIRA. Retrabalho é quando um **CARD**, se encontra na coluna Planejados/Reprovados, e está com o status 'Reprovado'.",
        verbose=True,
        allow_delegation=False
    )
    return rework_agent


rework_agent_task = Task(
    description="""
        Realize uma consulta no arquivo PDF vinculado a você, que contém informações 
        detalhadas sobre o processo de criação de RDOs na plataforma Opus. 
        A tarefa é buscar e fornecer uma resposta clara com base no conteúdo 
        do documento para responder a pergunta do usuário {question}. Certifique-se de responder apenas o que você encontrar no documento.
    """,
    expected_output="""
        Uma resposta detalhada e informativa que aborda a questão apresentada, 
        extraindo as informações diretamente do PDF. 
        A resposta deve ser clara, técnica quando necessário, e fácil de entender, 
        com foco em explicar o processo de criação de RDOs.
        A resposta Final deve ser em forma de parágrafo e não em tópicos.
    """,
    agent=rework_agent  
)