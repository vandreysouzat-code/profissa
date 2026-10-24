# Profissa

**Uma aplicação web desenvolvida para organizar informações e registros profissionais.**

O Profissa é um projeto desenvolvido com Python e Flask, utilizando SQLite para armazenamento de dados e HTML/CSS para a interface. Este repositório registra a evolução do projeto e seu desenvolvimento.

## Tecnologias

- Python
- Flask
- SQLite
- HTML
- CSS

## Funcionalidades

O sistema possui estrutura de aplicação web com:

- Cadastro e autenticação de usuários.
- Área de painel após o login.
- Módulos para organização de registros.
- Criação e visualização de registros associados ao usuário.
- Exclusão de registros.

Consulte o código-fonte para conhecer a implementação e os detalhes de cada funcionalidade.

## Executar localmente

### Pré-requisitos

- Python instalado.
- Git instalado (opcional, para clonar o repositório).

### Instalação

Clone o repositório:

```bash
git clone https://github.com/vandreysouzat-code/profissa.git
cd profissa
```

Crie e ative um ambiente virtual.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute a aplicação conforme a configuração definida em `app.py`.

> Não compartilhe credenciais nem dados reais durante os testes. Para disponibilizar a aplicação publicamente, configure adequadamente os segredos e o armazenamento persistente do banco de dados.

## Estrutura do projeto

```text
Profissa/
├── app.py
├── requirements.txt
├── static/
├── templates/
├── tests/
├── .gitignore
└── README.md
```

A estrutura pode evoluir conforme novas funcionalidades forem adicionadas.

## Testes

Os testes automatizados ficam no diretório `tests/`. Consulte os arquivos dessa pasta para verificar como executá-los.

## Segurança e dados

- Não envie senhas, tokens, arquivos `.env` ou bancos de dados com informações pessoais ao repositório.
- O banco de dados local e os arquivos de ambiente devem permanecer fora do controle de versão.
- Antes de usar o sistema em produção, revise autenticação, configuração de segredos, permissões e persistência dos dados.

## Autor

**Victor Andrey**  
GitHub: [@vandreysouzat-code](https://github.com/vandreysouzat-code)

## Direitos autorais

Copyright © 2026 Victor Andrey. Todos os direitos reservados.

O uso, a cópia, a modificação e a redistribuição deste software estão sujeitos aos termos da licença incluída neste repositório.

Consulte o arquivo `LICENSE` antes de utilizar o código.

---

Projeto em desenvolvimento.
