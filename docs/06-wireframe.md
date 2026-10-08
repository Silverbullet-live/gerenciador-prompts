# 6. Protótipo: o que levantamos vira tela antes do código

| O que levantamos | Vira no protótipo | No gerenciador da Fashion Co. |
|---|---|---|
| Requisitos funcionais | Ações: botões, campos, menus | Botão "Salvar prompt" · campo de busca por coleção |
| Requisitos não funcionais | Restrições do desenho | Tela pensada para o celular · confirmação em até 2 segundos |
| Casos de uso | Fluxos: telas em sequência | Salvar → buscar → reusar trocando os looks → aprovar → entregar |
| Modelo de domínio | Conteúdo: cartões, filtros, campos | Coleção → filtro · Prompt → cartão com selo "aprovado" · Look → campo |
| Histórias de usuário | Roteiro do teste com o usuário | "Encontre o prompt aprovado do verão e troque os looks" |

## Wireframe do mural (baixa fidelidade)

Feito antes de qualquer código, para validar com o "cliente" o que aparece na tela.

```
+------------------------------------------------------------------+
|  MURAL DE PROMPTS · FASHION CO.                  ● ao vivo   12  |
|  [Todas] [Verão 2027] [Inverno 2027] ...                         |
+------------------------------------------------------------------+
|  +------------------------+  +------------------------+          |
|  | VERÃO 2027  ★aprovado  |  | VERÃO 2027             |          |
|  | Editorial de praia     |  | Fundo de estúdio       |          |
|  | ...A modelo veste      |  | ...A modelo veste      |          |
|  | [{{look}}]. Enquadra...|  | [{{look}}], de frente..|          |
|  | — apelido · há 2 min   |  | — apelido · há 6 min   |          |
|  |              [ocultar] |  |              [ocultar] |          |
|  +------------------------+  +------------------------+          |
+------------------------------------------------------------------+
|  Para salvar, diga ao Claude:                                    |
|  "salva esse prompt na coleção ___"                    [QR code] |
+------------------------------------------------------------------+
```

### Decisões tomadas no wireframe

- **Texto grande:** o mural é lido de longe, no projetor.
- **O cartão mostra só um trecho:** o prompt completo se obtém pelo Claude, em `.prompt`.
- **O `{{look}}` em destaque:** é onde a peça muda quando o prompt é reusado.
- **Selo "aprovado":** o padrão da coleção se reconhece de longe (borda dourada).
- **A instrução de uso fica fixa no rodapé,** para quem chega atrasado.

## Três ferramentas, uma para cada nível de fidelidade

| Fidelidade | Ferramenta | Para quê |
|---|---|---|
| Baixa | **Excalidraw** | O rabisco digital, para combinar a ideia em minutos. |
| Média e alta | **Figma** | Padrão do mercado: protótipo clicável, em equipe. |
| Da descrição à tela | **Claude Design** | Descreve a tela com os requisitos; a IA gera a primeira versão. |

## Atividade

**Rabisque a tela de busca de prompts** que o editor de moda veria se o projeto tivesse um app próprio. Que campos ela tem? Como aparece o prompt aprovado? O que acontece quando a busca não encontra nada?

Depois, faça o teste com um colega usando o roteiro: *"Encontre o prompt aprovado do verão e troque os looks"*. Onde ele travou? Isso é um requisito que faltava.
