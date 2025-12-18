from main import LLM
from rich.console import Console
console=Console()
llm=LLM()

llm.select_model()
while True:
    user_prompt=input("ask any question (q to exit): ")
    if user_prompt.lower() == 'q':
        break
    llm.chat(user_prompt)
    