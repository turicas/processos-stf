# Processos do STF

Esse programa baixa os processos do Supremo Tribunal Federal brasileiro. A
estratégia é a seguinte:

- Para cada dia do intervalo desejado, lista todas as atas disponíveis;
- Para cada ata encontrada, lista os processos da ata;
- Para cada processo encontrado, baixa a página de detalhes do processo e
  extrai os dados.


## Instalando

Requer Python3.6+ instalado. Instale as dependências com:

```bash
pip install -r requirements.txt
```


## Rodando

```bash
./run.sh
```

Os dados ficarão disponíveis em `data/output/`.


## Dados

Por padrão, dois arquivos são criados:

- `data/output/lista-processos.csv`: contém dados superficiais sobre o
  processo, baseado na listagem que aparece na página da ata. Alguns campos
  podem vir em branco nessa tabela enquanto estão preenchidos na página do
  processo - recomenda-se utilizar o arquivo `data/output/processos.csv`;
- `data/output/processos.csv`: contém informações retiradas da página de
  detalhes do processo (nem todos os dados estão sendo salvos, como todos os
  andamentos).

> Nota: o identificador único é o número do processo e sua classe; esse par
> pode aparecer mais de uma vez se o processo for redistribuído.
