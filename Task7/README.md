### Описание

Для оценки используется техника LLM-as-a-judge - просим модель от OpenAI сравнить ответы с эталонными, назначив score и прокомментировать разницу.  

В качестве эталона тоже использовались ответы модели OpenAI на полноценной базе знаний, оценивались ответы, которые выдавала:  

* Локальная модель с неполной базой знаний
* Локальная модель
* OpenAI с неполной с неполной базой знаний

Анализ производился рядом скриптов:  

* ```ask.sh``` - задаёт вопросы из ```golden-set.txt``` локальной модели и OpenAI, записывает вопросы и ответы в пару файлов ```answers-local.jsonl``` и ```answers-openai.jsonl``` соответственно
* ```make_dataset.py``` - склеивает два jsonl-файла в формате предыдущего скрипта и делает jsonl с вопросом и парой ответов - эталон и оцениваемый ответ
* ```evaluate.sh``` - передаёт файл с вопросом, эталонным и оцениваемым ответами в модель OpenAI с промптом - просьбой оценить ответ по шкале 1 - 0.8 - 0.5 - 0.0 и описать причину
* ```semantic-similarity.sh``` - считает косинусное расстояние между эмбеддингами эталонного и оцениваемого ответов, эмбеддинги строятся только локальной моделью

Надо понимать, что такой способ не подойдёт для Production-решения из задачи т.к. произойдёт утечка данных.  

Для Production-решения можно попробовать сравнить эмбеддинги эталонного (предоставленного экспертами) ответа и оцениваемого ответов, а также просто привлечь экспертов на ограниченном объёме вопросов по разным темам.

### Оценка

Задаём вопросы на полной базе знений:

```
./ask.sh
```

Сохраняем результаты:

```
cp answers-local.jsonl answers-local-orig.jsonl
cp answers-openai.jsonl answers-openai-orig.jsonl
```

Удаляем ключевые статьи:

```
mv ../Task2/knowledge_base/Слои\ Мрака.txt /tmp/
mv ../Task2/knowledge_base/Пакт.txt /tmp
mv ../Task2/knowledge_base/Контроль.txt /tmp
```

Перестраиваем коллекцию Qdrant:

```
../Task3/index.sh

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

Задаём вопросы на неполной базе знений:

```
./ask.sh
```

Генерируем файлы с парами эталон-факт, в качестве эталона везде берутся ответы OpenAI на полной базе и отдаём на оценку модели OpenAI.  


Локальная модель, неполная база:

```
python make_dataset.py answers-local.jsonl answers-openai-orig.jsonl > reference-local-cut-vs-openai.jsonl

./evaluate.sh reference-local-cut-vs-openai.jsonl | tee evaluation-local-cut-vs-openai.jsonl
``

Модель OpenAI, неполная база:

```
python make_dataset.py answers-openai.jsonl answers-openai-orig.jsonl > reference-openai-cut-vs-openai.jsonl

./evaluate.sh reference-openai-cut-vs-openai.jsonl | tee evaluation-openai-cut-vs-openai.jsonl
```

Локальная модель, полная база:

```
python make_dataset.py answers-local-orig.jsonl answers-openai-orig.jsonl > reference-local-vs-openai.jsonl

./evaluate.sh reference-local-vs-openai.jsonl | tee evaluation-local-vs-openai.jsonl
```

Смотрим семантическую близость ответов - расстояние между эмбеддингами эталона и оцениваемого ответа, модель эмбеддингов - локальная.

Локальная модель, неполная база:

```
./semantic-similarity.sh reference-local-cut-vs-openai.jsonl | tee semantic-similarity-local-cut-vs-openai.jso
```

Локальная модель, полная база:

```
./semantic-similarity.sh reference-local-vs-openai.jsonl | tee semantic-similarity-local-vs-openai.jsonl
```

### Анализ результатов


