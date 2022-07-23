# mqu-travelling-salesman-metaheuristics
Trabalho sobre metaheurísticas aplicadas ao problema do caixeiro viajante para a disciplina de Métodos Quantitativos (Bacharelado em Engenharia de Software, CEAVI)

## Como executar

Primeiro instalar as dependências

```
pip install -r requirements.txt
```

Para executar os algoritmos e gerar estatísticas, temos o script `stats.py`. Ele pode ser chamado com várias combinações de _flags_ de linha de comando para selecionar quais algoritmos executar, quais instâncias utilizar, quais os critérios de parada dos algoritmos etc.

Para obter a relação das _flags_ e algoritmos e instâncias disponíveis

```
py stats.py -h
```

Exemplo de utilização (alterando parâmetros de execução)

```
py stats.py --runs 5 --algos RAND,SLSF,SLSB --instances kroA100,kroA150,brazil58 --criterion time,60 --supercriterion time,60 --subcriterion iters,1000 --out teste.json
```

Exemplo de utilização (alterando parâmetros dos algorimos)

```
py stats.py --rlsprob 0.1 --alpha 0.6 --ilsperc 0.5
```
