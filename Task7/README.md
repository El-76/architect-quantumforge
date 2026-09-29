./ask.sh

cp answers-local.jsonl answers-local-orig.jsonl
cp answers-openai.jsonl answers-openai-orig.jsonl

rm ../Task2/knowledge_base/Слои\ Мрака.txt
rm ../Task2/knowledge_base/Пакт.txt
rm ../Task2/knowledge_base/Контроль.txt

../Task3/index.sh

```
Building embeddings with local model...
2026-09-29 14:50:25 | INFO     | started processing 3 new, changed or deleted wiki pages
2026-09-29 14:50:25 | INFO     | successfully uploaded 0 chunks from 0 new or changed wiki pages, 3 pages deleted, total collection size is 108

real    0m15.479s
user    0m7.723s
sys     0m3.440s

Building embeddings with OpenAI...
2026-09-29 14:50:35 | INFO     | started processing 3 new, changed or deleted wiki pages
2026-09-29 14:50:35 | INFO     | successfully uploaded 0 chunks from 0 new or changed wiki pages, 3 pages deleted, total collection size is 130

real    0m9.883s
user    0m8.538s
sys     0m1.638s
```

./ask.sh

python make_dataset.py answers-local.jsonl answers-openai-orig.jsonl > reference-local-cut-vs-openai.jsonl

./evaluate.sh reference-local-cut-vs-openai.jsonl | tee evaluation-local-cut-vs-openai.jsonl

python make_dataset.py answers-openai.jsonl answers-openai-orig.jsonl > reference-openai-cut-vs-openai.jsonl

./evaluate.sh reference-openai-cut-vs-openai.jsonl | tee evaluation-openai-cut-vs-openai.jsonl

python make_dataset.py answers-local-orig.jsonl answers-openai-orig.jsonl > reference-local-vs-openai.jsonl

./evaluate.sh reference-local-vs-openai.jsonl | tee evaluation-local-vs-openai.jsonl



maaaah@debian:~/architect-quantumforge/Task7$ ../Task4/rag_query.sh 'Есть ли договорённости между Дневными и Ночными?'
Invalid model-index. Not loading eval results into CardData.
Answer:
Действительно, между Дневными и Ночной сторонами заключен "Великий Пакт о перемирии".
maaaah@debian:~/architect-quantumforge/Task7$ ../Task4/rag_query.sh --openai-embeddings --openai-llm 'Есть ли договорённости между Дневными и Ночными?'
Invalid model-index. Not loading eval results into CardData.
Answer:
Да. Дневные и Ночные Другие подписали **«Великий Пакт о перемирии»**, чтобы не уничтожить друг друга. За его соблюдением следит **Контроль**, состоящий из Дневных и Ночных колдунов.
maaaah@debian:~/architect-quantumforge/Task7$ vim README.md
maaaah@debian:~/architect-quantumforge/Task7$ ../Task4/rag_query.sh 'Еcть ли какая-то третья сила, помимо Дневных и Ночных?'                                 Invalid model-index. Not loading eval results into CardData.
Answer:
Ничего подобного нет в базе знаний.
maaaah@debian:~/architect-quantumforge/Task7$ ../Task4/rag_query.sh --openai-embeddings --openai-llm 'Еcть ли какая-то третья сила, помимо Дневных и Ночных?'Invalid model-index. Not loading eval results into CardData.
Answer:
Согласно базе знаний, третья сила не упоминается: существуют две Первородные Энергии — День и Ночь, которым соответствуют Дневные и Ночные Другие.
maaaah@debian:~/architect-quantumforge/Task7$ ../Task4/rag_query.sh 'Ограничивает ли кто-то Дневных и Ночных в своих действиях?'                             Invalid model-index. Not loading eval results into CardData.
Answer:
Дневные и Ночные имеют свои собственные принципы поведения:

1. **Дневные**:
   - Они обычно являются альтруистами.
   - Не склонны хотеть изменять мир.
   - Свобода воли; свобода действовать так, как они хотят этого сам.

2. **Ночные**:
   - Наоборот, ярко выраженные эгоисты и индивидуалисты.
   - Главная ценность для них — свобода.
   - Не стремятся менять мир.
   - В отличии от Дневных, они предпочитают быть свободными без необходимости найти моральные обоснования.

Таким образом, эти две группы людей ограничивают друг друга по своим ценностям и принципам поведения.
maaaah@debian:~/architect-quantumforge/Task7$ ../Task4/rag_query.sh --openai-embeddings --openai-llm 'Ограничивает ли кто-то Дневных и Ночных в своих действиях?'
Invalid model-index. Not loading eval results into CardData.
Answer:
Да. Действия Дневных и Ночных ограничивает Великий Пакт: вмешательство Дневных в жизнь людей ограничено его условиями, а совершённое ими вмешательство может дать Ночным право на аналогичное по энергии вмешательство.

Кроме того, их сдерживает баланс между Днём и Ночью. Чрезмерное усиление Дня в конечном итоге может привести к появлению Отражения и серьёзному ущербу Дню. У Ночных также есть идеологические ограничения, но конкретный механизм контроля их действий в базе знаний не описан.
maaaah@debian:~/architect-quantumforge/Task7$ ../Task4/rag_query.sh 'Контролирует ли кто-то Дневных и Ночных?'                                               Invalid model-index. Not loading eval results into CardData.
Answer:
Да, контролируется Дневными и Ночными. Контроль состоит как из Ночных, так и из Дневных колдунов.
maaaah@debian:~/architect-quantumforge/Task7$ ../Task4/rag_query.sh --openai-embeddings --openai-llm 'Контролирует ли кто-то Дневных и Ночных?'
Invalid model-index. Not loading eval results into CardData.
Answer:
Да. За соблюдением Великого Пакта о перемирии следит **Контроль**, состоящий из Дневных и Ночных колдунов. Он карает нарушителей пакта.

Кроме того, **Чёрный Патруль** из Дневных следит за Ночными, а **Белый Патруль** из Ночных — за Дневными.

maaaah@debian:~/architect-quantumforge/Task7$ ../Task4/rag_query.sh 'Сколько слоёв во мраке?'
Invalid model-index. Not loading eval results into CardData.
Answer:
Мрак состоит из нескольких слоёв: первый, второй и шестой.
maaaah@debian:~/architect-quantumforge/Task7$ ../Task4/rag_query.sh --openai-embeddings --openai-llm 'Сколько слоёв во мраке?'
Invalid model-index. Not loading eval results into CardData.
Answer:
В Мраке шесть слоёв.
