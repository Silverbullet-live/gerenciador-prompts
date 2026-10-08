# 3. Diagrama de classes

Ponto de partida: a classe `Prompt` do livro da Chip Huyen (cap. 5), escrita em Python com Pydantic:

```python
class Prompt(BaseModel):
    model_name: str
    date_created: datetime
    prompt_text: str
    application: str
    creator: str
```

Ela já é, quase, um diagrama de classes. Abaixo, a versão deste projeto.

## Versão 1 (o que está implementado)

```mermaid
classDiagram
    class Prompt {
        +string id
        +string titulo
        +string texto
        +string categoria
        +string autor
        +string modelo
        +number temperatura
        +Date criadoEm
        +boolean oculto
        +paraDotprompt() string
    }
    class Categoria {
        +string nome
        +number total
    }
    Categoria "1" --> "*" Prompt : agrupa
```

Na versão 1, `Categoria` não é guardada à parte: ela é **derivada** dos prompts (o sistema conta quantos prompts há em cada categoria). Isso é uma decisão de projeto que vale discutir.

## Atividade: versão 2

O livro aponta um problema: se várias aplicações usam o mesmo prompt e ele é alterado, todas mudam juntas. Como resolver? Uma resposta possível:

```mermaid
classDiagram
    class Prompt {
        +string id
        +string titulo
        +string categoria
        +versaoAtual() Versao
    }
    class Versao {
        +number numero
        +string texto
        +string modelo
        +Date criadaEm
        +string motivoDaMudanca
    }
    class Aplicacao {
        +string nome
        +number versaoFixada
    }
    Prompt "1" *-- "1..*" Versao : tem
    Aplicacao "*" --> "1" Prompt : usa
```

Cada aplicação **fixa** a versão que usa. Uma mudança no prompt cria uma `Versao` nova sem quebrar quem depende da antiga.
