# 4. Diagrama de sequência

O caminho de uma frase, da conversa ao mural.

```mermaid
sequenceDiagram
    actor E as Estudante<br/>(editor de moda)
    participant C as App do Claude
    participant S as Servidor MCP<br/>(Firebase Functions)
    participant DB as Banco<br/>(Firestore)
    participant M as Mural<br/>(projetor)

    E->>C: "salva esse prompt na coleção Verão 2027"
    C->>C: escolhe salvar_prompt
    C->>S: salvar_prompt(título, texto, coleção, apelido)
    S->>S: valida (tamanho, campos obrigatórios)
    alt dados válidos
        S->>DB: grava a coleção (se for nova) e o prompt
        DB-->>S: id
        S-->>C: "salvo, id abc123"
        C-->>E: "Pronto! Salvei na coleção Verão 2027."
        DB-)M: aviso em tempo real
        M->>M: mostra o novo cartão no topo
    else dados inválidos
        S-->>C: erro com o motivo
        C-->>E: explica o que corrigir
    end
```

## Perguntas para a turma

1. Quem decide chamar `salvar_prompt`: o estudante ou o Claude?
2. O mural pergunta ao banco se há novidade (*polling*) ou o banco avisa o mural (*push*)? Que requisito não funcional isso atende? (Dica: RNF01.)
3. Onde, nesta sequência, ficaria a verificação de login da versão 2?
4. Desenhe a sequência de `aprovar_prompt`. Quantas mensagens ela tem a mais que a de salvar? (Dica: o antigo padrão volta a rascunho.)
