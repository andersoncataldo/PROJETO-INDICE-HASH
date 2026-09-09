# Índice Hash Estático

Projeto acadêmico de Banco de Dados que simula a organização de uma tabela em páginas e a construção de um índice hash estático em memória. A aplicação possui uma interface gráfica para carregar palavras, configurar a paginação e os buckets, construir o índice e comparar uma busca indexada com um table scan.

## Requisitos

- Python 3.10 ou superior
- Tkinter, normalmente incluído na instalação do Python

O projeto utiliza apenas a biblioteca padrão do Python. No Linux, pode ser necessário instalar o pacote do Tkinter, por exemplo:

```bash
sudo apt-get install python3-tk
```

## Como executar

Na raiz do projeto, execute:

```bash
python main.py
```

No Windows, também é possível usar:

```powershell
py main.py
```

A janela permite selecionar outro arquivo `.txt`, limitar a quantidade de palavras carregadas e escolher como a tabela será paginada.

## Fluxo da aplicação

1. O arquivo de dados é lido pelo módulo `data_loader`.
2. As palavras são divididas em páginas de tamanho configurável.
3. Cada palavra recebe um endereço de bucket por meio da função hash escolhida.
4. O índice é construído, registrando colisões e encadeando buckets de overflow quando necessário.
5. A aplicação exibe as páginas, as estatísticas do índice e permite realizar buscas.
6. A mesma chave pode ser procurada pelo índice hash e por table scan para comparar custo e tempo.

## Conceitos implementados

### Paginação

Os registros são organizados em páginas sequenciais. É possível informar diretamente o número de registros por página ou a quantidade desejada de páginas. As páginas são numeradas a partir de `0`.

### Índice hash

Para cada chave, a função hash calcula um endereço entre `0` e `NB - 1`, onde `NB` é o número de buckets principais. Cada bucket comporta até `FR` entradas.

- **Colisão:** duas ou mais chaves são direcionadas ao mesmo bucket.
- **Overflow:** um bucket cheio precisa criar ou usar um bucket adicional encadeado.
- **Fator de carga:** controla a folga média dos buckets. Valores menores criam mais buckets e tendem a reduzir overflows.

As funções disponíveis são `djb2`, recomendada para as palavras do projeto, e uma soma simples dos códigos ASCII, disponível para comparação.

### Busca e table scan

A busca indexada calcula diretamente o bucket da chave e percorre apenas sua cadeia de overflow. O custo considera os buckets acessados e, quando a chave é encontrada, a leitura da página de dados.

O table scan percorre as páginas em ordem até encontrar a chave ou chegar ao final da tabela. A interface mostra a quantidade de páginas percorridas e compara os dois métodos.

## Parâmetros da interface

- **Arquivo de dados:** caminho do arquivo com uma palavra por linha.
- **Limite de palavras:** opcional; útil para testes rápidos com apenas as primeiras palavras.
- **Tamanho da página:** número de registros por página.
- **Quantidade de páginas:** alternativa ao tamanho fixo da página.
- **FR:** número máximo de entradas em cada bucket.
- **Função hash:** algoritmo usado para calcular os endereços.
- **Fator de carga:** número entre `0` e `1` que define a ocupação média desejada.

## Estrutura do projeto

```text
indice_hash/
├── main.py
├── data/
│   └── words.txt
└── src/
    ├── bucket.py
    ├── data_loader.py
    ├── gui.py
    ├── hash_function.py
    ├── indice_hash.py
    └── pagina.py
```

### Arquivos

- [`main.py`](main.py): ponto de entrada da aplicação. Configura o caminho de `src/` e inicia a interface gráfica.
- [`src/gui.py`](src/gui.py): implementa a interface Tkinter, a leitura das configurações, a construção em segundo plano, as abas de páginas e estatísticas e as operações de busca e table scan.
- [`src/data_loader.py`](src/data_loader.py): lê o arquivo de texto, remove linhas vazias e retorna as palavras; também permite limitar a quantidade carregada.
- [`src/pagina.py`](src/pagina.py): define a classe `Pagina` e as funções para calcular a quantidade ou o tamanho das páginas e dividir os registros.
- [`src/hash_function.py`](src/hash_function.py): contém as funções hash `djb2` e soma simples, além do catálogo usado pela interface.
- [`src/bucket.py`](src/bucket.py): define `Entrada` e `Bucket`, incluindo inserção, busca e encadeamento de buckets de overflow.
- [`src/indice_hash.py`](src/indice_hash.py): coordena a construção do índice, calcula `NB`, executa buscas indexadas, realiza table scans e produz estatísticas.
- [`data/words.txt`](data/words.txt): arquivo de dados padrão, com uma palavra por linha.

## Observações

O índice e as páginas são mantidos apenas em memória durante a execução. Ao fechar a aplicação, eles são descartados e precisam ser reconstruídos na próxima execução.