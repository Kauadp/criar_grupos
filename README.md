# Criar Grupos WhatsApp - EXAGERADO

Automatize a criação de grupos no WhatsApp para o evento **EXAGERADO** (Carapina), facilitando a organização dos expositores, controle de vendas e comunicação eficiente entre equipes.

## Visão Geral

O projeto recebe uma planilha de vendas dos stands do evento, trata os dados, e utiliza a [Z-API](https://z-api.io/) para criar grupos no WhatsApp automaticamente. Cada grupo inclui o expositor responsável, além de dois participantes fixos: **Financeiro** e **Sucesso do Cliente**.

## Fluxo de Funcionamento

1. **Tratamento dos Dados (`scirpt_tratar_dados.R`):**
   - Processa a planilha `stand_es.csv` localizada em `dados/`.
   - Gera o arquivo `dados_grupo.JSON` com informações de grupos e contatos.
   - Pode usar `icon.txt` para personalizar o ícone dos grupos (em base64).

2. **Criação dos Grupos (`criar_grupos.py`):**
   - Utiliza o arquivo `dados_grupo.JSON` e a Z-API para criar grupos no WhatsApp.
   - Para cada grupo:
     - Adiciona o expositor.
     - Adiciona dois contatos fixos: **Financeiro** e **Sucesso do Cliente**.
     - Pode definir ícone do grupo via API, conforme o arquivo `icon.txt`.

## Estrutura de Pastas e Arquivos

```
├── scirpt_tratar_dados.R      # Script R para tratamento da planilha e geração do JSON
├── criar_grupos.py            # Script Python para integração com a Z-API e criação dos grupos
├── dados/
│   ├── dados_grupo.JSON       # Arquivo gerado contendo dados dos grupos e contatos
│   ├── stand_es.csv           # Planilha completa de controle de vendas dos stands
│   └── icon.txt               # Ícone dos grupos (base64)
└── README.md                  # Documentação do projeto
```

## Requisitos

- **R:** Para rodar o tratamento de dados.
- **Python 3:** Para rodar a automação via Z-API.
- Conta ativa na [Z-API](https://z-api.io/).
- Instalar dependências conforme instruções nos scripts.

## Passo a Passo

1. **Prepare** a planilha `stand_es.csv` em `dados/` no formato utilizado pelo evento.
2. **Execute** o script R `scirpt_tratar_dados.R` para gerar `dados_grupo.JSON`.
3. **(Opcional)** Prepare o arquivo `icon.txt` com uma imagem em base64 para ser usada como ícone dos grupos.
4. **Execute** o script Python `criar_grupos.py` para criar automaticamente os grupos e adicionar os participantes.

## Observações

- Os contatos de **Financeiro** e **Sucesso do Cliente** devem ser configurados no script Python.
- O projeto foi desenvolvido durante o estágio no evento **EXAGERADO** e pode ser adaptado para outros cenários de automação de grupos.

## Contribuição

Sugestões e melhorias são bem-vindas! Abra issues ou pull requests para colaborar.

---

**Autor:** [Kauadp](https://github.com/Kauadp)