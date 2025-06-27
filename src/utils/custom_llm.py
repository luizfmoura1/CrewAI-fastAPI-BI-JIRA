import requests
import json
from typing import Any, List, Optional
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import SimpleChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage

def _message_to_dict(message: BaseMessage) -> dict:
    """Converte uma mensagem LangChain para o formato de dicionário da API."""
    if isinstance(message, HumanMessage):
        role = "user"
    elif isinstance(message, AIMessage):
        role = "assistant"
    elif isinstance(message, SystemMessage):
        role = "system"
    else:
        raise ValueError(f"Tipo de mensagem desconhecido: {message}")
    return {"role": role, "content": message.content}

class ChatDatabricks(SimpleChatModel):
    """
    Cliente de Chat customizado para chamar um endpoint de modelo no Databricks
    que seja compatível com a API da OpenAI (como o Llama 3).
    """
    endpoint_url: str
    token: str
    temperature: float = 0.7
    max_tokens: int = 10000 

    def _call(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        message_dicts = [_message_to_dict(m) for m in messages]

        payload = {
            "messages": message_dicts,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        response = requests.post(self.endpoint_url, headers=headers, data=json.dumps(payload))
        
        # Lança um erro se a resposta não for bem-sucedida (ex: 401, 404, 500)
        response.raise_for_status() 

        response_json = response.json()
        
        # A estrutura de resposta do Databricks para modelos foundation segue este padrão
        content = response_json["choices"][0]["message"]["content"]
        
        return content