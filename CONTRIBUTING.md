# Como colaborar

Este guia leva você do **fork** ao **pull request**, passo a passo, e mostra o que fazer quando algo dá errado. Se travar, procure a mensagem de erro na seção [Erros comuns](#erros-comuns): quase sempre é um passo pulado, e não um problema do projeto.

## Antes de começar

- Uma conta no [GitHub](https://github.com).
- O **Git** instalado. Para conferir, abra o terminal e digite `git --version`. Se aparecer um número de versão, está pronto. Se não, instale em [git-scm.com](https://git-scm.com).
- Para enviar código ao GitHub pelo terminal, você vai precisar entrar com a sua conta. O jeito mais simples é o [GitHub CLI](https://cli.github.com): depois de instalado, rode `gh auth login` uma vez.

## O caminho, do fork ao pull request

### 1. Fork: a sua cópia no GitHub

1. Abra [github.com/brevvi/gerenciador-prompts](https://github.com/brevvi/gerenciador-prompts).
2. Clique em **Fork**, no canto superior direito.
3. Em **Owner**, escolha a sua conta (ou a do grupo) e clique em **Create fork**.

O fork é uma cópia do projeto na **sua** conta. Você pode mudar o que quiser nele sem afetar o original.

Em grupo: um integrante cria o fork e adiciona os colegas em **Settings → Collaborators**.

### 2. Clone: a cópia no seu computador

Escolha uma pasta para guardar o projeto e rode:

```bash
git clone https://github.com/<sua-conta>/gerenciador-prompts.git
cd gerenciador-prompts
git remote add upstream https://github.com/brevvi/gerenciador-prompts.git
```

- O endereço do `git clone` é o **do seu fork**, com a **sua** conta no lugar de `<sua-conta>`. Ele aparece no botão verde **Code** da página do fork.
- O `cd` é obrigatório: o clone cria uma pasta, e todos os comandos seguintes rodam **dentro dela**.
- O `upstream` aponta para o projeto original. É de lá que vêm as novidades (ver o passo 6).
- **Não rode `git init`.** O `git init` cria um repositório novo, do zero. O clone já traz um repositório pronto.

Para conferir: `git remote -v` deve mostrar o `origin` (o seu fork) e o `upstream` (o original).

### 3. Branch: um ramo por tarefa

```bash
git switch -c <nome-da-tarefa>
```

Dê à branch o nome da tarefa, por exemplo `login` ou `corrige-busca`. Assim, cada mudança fica separada e a `main` continua limpa.

### 4. Commit e push: registrar e enviar

Faça a sua mudança nos arquivos, salve, e então:

```bash
git add <arquivos que você mudou>
git commit -m "Uma frase que diga o que mudou"
git push -u origin <nome-da-tarefa>
```

- O `git add` escolhe o que vai no commit; o `git commit` registra; o `git push` envia ao GitHub.
- O `-u origin <nome-da-tarefa>` só é necessário **no primeiro envio** de cada branch. Depois, basta `git push`.

### 5. Pull request: pedir para a mudança entrar

1. Depois do push, abra a página do seu fork no GitHub. Vai aparecer um aviso com o botão **Compare & pull request**.
2. Confira o destino: `brevvi/gerenciador-prompts`, branch `main`.
3. No texto, explique **o problema e a solução**. Se o pull request resolve uma issue, escreva `fecha #<número>`: ela será fechada sozinha quando a mudança for aceita.
4. Clique em **Create pull request**.

A partir daí, quem mantém o projeto revisa, comenta e, se estiver tudo certo, faz o merge.

### 6. Manter o fork em dia

Antes de começar uma tarefa nova, traga as novidades do projeto original:

- **Pelo site:** na página do seu fork, clique em **Sync fork → Update branch**. Depois, no computador, `git switch main` e `git pull`.
- **Pelo terminal:**
  ```bash
  git switch main
  git pull upstream main
  git push
  ```

## O que entra no projeto original

| Entra no original (por pull request) | Fica no seu fork |
|---|---|
| Correções e melhorias pequenas, cada uma ligada a uma issue, com o teste e a análise (`docs/`) atualizados | Os desafios v2, v3 e v4: são de vocês. Mostre o resultado deixando o link do fork numa issue |

Antes de abrir o pull request, rode os testes: `cd functions && npm install && npm test`.

## Erros comuns

| Mensagem | O que aconteceu | Como resolver |
|---|---|---|
| `fatal: not a git repository (or any of the parent directories): .git` | Você não está dentro da pasta do projeto. Talvez o clone ainda não tenha sido feito, ou faltou o `cd` depois dele | Rode o `git clone` e depois `cd gerenciador-prompts` |
| `fatal: The current branch <nome> has no upstream branch.` | É o primeiro envio da branch, e o Git não sabe para onde mandar | `git push -u origin <nome>`. Para não ver mais esse erro: `git config --global push.autoSetupRemote true` |
| `Support for password authentication was removed` ou `Authentication failed` | O GitHub não aceita mais a senha da conta no terminal | Rode `gh auth login` (GitHub CLI) e tente de novo |
| `Permission to brevvi/gerenciador-prompts.git denied` | Você clonou o **original**, e não o seu fork. Só quem mantém o projeto pode enviar direto para ele | Aponte o `origin` para o seu fork: `git remote set-url origin https://github.com/<sua-conta>/gerenciador-prompts.git` |
| `nothing to commit, working tree clean` | Não há mudança para registrar: o arquivo não foi salvo, ou a mudança já está no último commit | Salve o arquivo e confira com `git status` |
| `Everything up-to-date` | Não há commit novo para enviar | Faça o commit antes do push |
| `fatal: destination path 'gerenciador-prompts' already exists` | O clone já foi feito antes nessa pasta | Só entre nela: `cd gerenciador-prompts` |
| Rodou `git init` por engano numa pasta que só guarda projetos | Essa pasta virou um repositório vazio, e o clone ficaria dentro de outro repositório | Confira que está na pasta certa e que ela não tem commits (`git log` responde *does not have any commits yet*), e apague o repositório vazio: `rm -rf .git` |

Ainda travou? Abra uma [issue](https://github.com/brevvi/gerenciador-prompts/issues) com a mensagem de erro completa e o comando que você rodou.
