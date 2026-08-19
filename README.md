# Índice Hash Estático — Trabalho de Banco de Dados

Aplicação com interface gráfica (Tkinter) que implementa e ilustra o
funcionamento de um **índice hash estático** sobre uma tabela simulada,
conforme especificação do Projeto 1 (Universidade de Fortaleza).

## Como executar

Requisitos: Python 3.10+ com Tkinter (já vem por padrão na maioria das
instalações; no Linux, se faltar: `sudo apt-get install python3-tk`).

```bash
python3 main.py
```

Nenhuma biblioteca externa é necessária — o projeto usa apenas a biblioteca
padrão do Python.

## Estrutura do projeto

```
indice_hash/
├── main.py                 # ponto de entrada
├── data/
│   └── words.txt            # 466.550 palavras (chaves), 1 por linha
├── src/
│   ├── pagina.py             # estrutura Página + cálculo de paginação
│   ├── bucket.py             # estrutura Bucket + colisão/overflow
│   ├── hash_function.py      # funções hash (djb2 e soma simples)
│   ├── indice_hash.py        # construção do índice, busca, table scan, estatísticas
│   ├── data_loader.py        # carga do arquivo de dados
│   └── gui.py                # interface gráfica (Tkinter)
└── README.md
```

## Como usar a interface

1. **Configuração**: escolha o arquivo de dados (já vem pré-preenchido com
   `data/words.txt`), defina a paginação por **tamanho da página** OU por
   **quantidade de páginas** (mutuamente exclusivos — só um é digitado, o
   outro é calculado automaticamente), defina o **FR** (tuplas por bucket) e
   a **função hash**. Opcionalmente, limite o número de palavras carregadas
   para testes rápidos.
2. Clique em **"Carregar dados e Construir Índice"**. A carga, paginação e
   construção do índice rodam em segundo plano (não travam a interface).
3. Aba **"1. Páginas carregadas"**: mostra a primeira e a última página.
4. Aba **"2. Estatísticas do índice"**: NR, NB, FR, número de páginas, total
   de inserções, colisões e overflows (contagem e taxa %).
5. Aba **"3. Busca e Table Scan"**: digite uma chave (uma palavra do arquivo)
   e clique em **Buscar** — mostra se foi encontrada, em qual página, o custo
   em acessos e o tempo. Depois disso o botão **Table Scan** é habilitado:
   ele percorre página por página até achar a mesma chave, mostrando o custo
   (páginas lidas) e o tempo. Por fim, é exibida a comparação de tempo/custo
   entre os dois métodos.

## Decisões de projeto

- **Colisão** é resolvida por encadeamento dentro do próprio bucket (até FR
  entradas). **Overflow** (bucket já com FR entradas) é resolvido por
  encadeamento de buckets extras de transbordamento (overflow chaining).
- **Função hash padrão**: `djb2` (polinomial), boa distribuição para strings.
  Uma segunda função (`soma simples dos códigos ASCII`) é oferecida de
  propósito para efeito de comparação — ela produz muito mais colisões e
  overflow, o que é útil para discutir na apresentação o impacto da escolha
  da função hash.
- **Custo de busca pelo índice** = nº de buckets acessados na cadeia de
  overflow + 1 acesso à página de dados encontrada.
- **Custo do table scan** = nº de páginas lidas até encontrar a chave (ou até
  o fim, se não encontrada) — não conta registro por registro, e sim página
  por página, como pede o enunciado (item 6d).
- A fonte de dados (`words.txt`) foi obtida em
  `https://github.com/dwyl/english-words` (arquivo `words.txt`, com 466.550
  linhas — bate com os "466 mil" citados no enunciado).
