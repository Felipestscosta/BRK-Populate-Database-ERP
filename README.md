# BRK Poupulador para Banco de Dados

Aplicação de linha de comando para migrar dados de uma planilha (CSV/XLS/XLSX)
para um banco SQLite.

## Requisitos

- Python 3.10+
- Dependências listadas em `requirements.txt`

Instale os requisitos com:

```bash
pip install -r requirements.txt
```

## Utilização

Execute o comando abaixo informando o caminho da planilha que contém os dados a
serem importados:

```bash
python importer.py caminho/para/planilha.csv
```

Também é possível importar planilhas `.xls` ou `.xlsx`:

```bash
python importer.py caminho/para/planilha.xls
```

Por padrão os dados serão gravados no arquivo SQLite `produtos_bling.db`, na
tabela `produtos_bling`. Para alterar o arquivo de banco de dados utilize a
opção `--banco`:

```bash
python importer.py caminho/para/planilha.csv --banco caminho/para/banco.db
```

### Estrutura do banco

- O arquivo do banco SQLite gerado é chamado `produtos_bling.db` (a menos que o
  argumento `--banco` seja informado).
- O script cria/atualiza a tabela `produtos_bling` com as colunas definidas na
  primeira linha da planilha.
- Registros são inseridos a partir da segunda linha da planilha.

### Observações

- Caso a tabela `produtos_bling` já exista, ela será recriada para refletir
  exatamente a estrutura da planilha importada.
- Valores vazios são gravados como `NULL` no banco de dados.
