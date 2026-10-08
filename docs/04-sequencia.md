# 4. Diagrama de sequência

O caminho que uma frase percorre do celular do estudante até o mural no projetor.

```mermaid
sequenceDiagram
    actor E as Estudante
    participant C as App do Claude
    participant S as Servidor MCP<br/>(Firebase Functions)
    participant DB as Firestore
    participant M as Mural<br/>(projetor)

    E->>C: "salva esse prompt na categoria marketing"
    C->>C: decide usar a ferramenta salvar_prompt
    C->>S: salvar_prompt(titulo, texto, categoria, autor)
    S->>S: valida (tamanho, campos obrigatórios)
    alt dados válidos
        S->>DB: grava documento em /prompts
        DB-->>S: id
        S-->>C: "Salvo com id abc123"
        C-->>E: "Pronto! Salvei na categoria marketing."
        DB-)M: atualização em tempo real
        M->>M: mostra o novo cartão no topo
    else dados inválidos
        S-->>C: erro com o motivo
        C-->>E: explica o que corrigir
    end
```

## Perguntas para a turma

1. Quem decide chamar `salvar_prompt`: o estudante ou o Claude?
2. O mural pergunta ao banco se há novidade (*polling*) ou o banco avisa o mural (*push*)? Que requisito não funcional isso atende?
3. Onde, nesta sequência, ficaria a verificação de login da versão 2?
