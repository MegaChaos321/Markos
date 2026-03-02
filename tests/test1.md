!Teste 1!

# Parte 1

Primeiro parágrafo desta parte. Este é um parágrafo médio. Lorem ipsum dolor sit
amet consectetur adipisicing elit. Est blanditiis incidunt, asperiores error
suscipit quas odio! Perferendis, commodi. Vel beatae sapiente, sed autem
excepturi temporibus sunt enim ducimus voluptate quaerat eligendi distinctio
nihil assumenda dolores similique fuga! Possimus, dolorum consectetur?

Outro parágrafo pequeno: Lorem ipsum dolor sit, amet consectetur adipisicing
elit. Quibusdam sapiente architecto blanditiis iure ullam hic!

## Parte 1.1

Outro parágrafo pequeno: Lorem ipsum dolor sit, amet consectetur adipisicing
elit. Quibusdam sapiente architecto blanditiis iure ullam hic!

Aqui fica um link "inline": [simulador de Markdown](http://daringfireball.net/projects/markdown/dingus "Dingus")

Agora vem um link em parágrafo à parte:

[lápis azul](https://twitter.com/ "Twitter - The Unofficial Censor ")

A seguir vem a *Parte 1.2*. Eis como introduzir uma sub-secção em **Markdown**:

\## Parte 1.2

(espero que o __compilador__ não tenha _gerado_ um h2 )
## Parte 1.2
Aqui começa o 1o parágrafo da Parte 1.2. No código MD, este parágrafo fica bem
coladinho ao título da secção.

# Parte 2 [DuckDuckGo](https://duckduckgo.com "DuckDuckGo: Alternativa ao Google")

Nesta parte tratamos de listas

## Parte 2.1

A seguir NÃO vem uma lista no dingus do Daring Fireball, mas VEM num dos
previews do VS Code e no código gerado pelo CommonMark:
- item 1
- item 2

Os itens seguintes já vão fazer parte da lista no dingus do Daring Fireball
(e nos outros compiladores também) porque estão separados deste parágrafo
por uma linha em branco:

- item 1
- item 2

- item 3
- item 4

  # Cabeçalho ainda dentro do item actual (pq está indentado)
- item 4.5

  Parágrafo dentro deste item. Linhas indentadas com 2 a 4 espaços geram
  um novo parágrafo.
  No código MD esta frase está chegada à esquerda, não há linha em branco a
  separá-la da última linha e como tal faz parte do parágrafo dentro deste item.
  O VS Code preserva as mudanças de linha com br's. Nós vamos ignorar.

Novo parágrafo dentro do item 4 no dingus do Daring Fireball, mas no VS Code
e no Common Mark termina a lista. A frase anterior teria que estar indentada com
pelo menos dois espaços à esquerda e não apenas um.

- item 5
* item 6 com outro símbolo
* item 7
  que continua na linha seguinte
- item 8 (último item da lista)

este parágrafo chegado ao início marca também o fim da lista anterior

agora vem um novo parágrafo

-isto não é uma lista  (não há espaço entre o '-' e o prim. car. da lista)

#

O '#' anterior marca uma secção sem título. No dingus do DaringFireball é
apenas um parágrafo. No VS Code e no CommonMark é um h1 vazio. Em geral,
nós vamos seguir o Common Mark.
