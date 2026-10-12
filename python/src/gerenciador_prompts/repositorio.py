"""Onde os prompts ficam guardados. Por enquanto, na memória."""

from gerenciador_prompts.modelo import Prompt


class RepositorioEmMemoria:
    """Guarda os prompts numa lista: some quando o servidor reinicia."""

    def __init__(self):
        self.prompts = []  # a "gaveta" deste repositório: começa vazia

    def salvar_prompt(self, prompt: Prompt) -> Prompt:
        """Guarda o prompt e o devolve."""
        self.prompts.append(prompt)
        return prompt
