### Описание

Для оценки используется техника LLM-as-a-judge - просим модель от OpenAI сравнить ответы с эталонными, назначив score и прокомментировать разницу.  

Также была сделана попытка посчитать семантическую близость эталонных и оцениваемых ответов.

Грубые метрики типа "длина ответа" не использовались.

В качестве эталона тоже использовались ответы модели OpenAI на полноценной базе знаний, оценивались ответы, которые выдавала:  

* Локальная модель с неполной базой знаний
* Локальная модель
* OpenAI с неполной с неполной базой знаний

Анализ производился рядом скриптов:  

* ```ask.sh``` - задаёт вопросы из ```golden-set.txt``` локальной модели и OpenAI, записывает вопросы и ответы в пару файлов ```answers-local.jsonl``` и ```answers-openai.jsonl``` соответственно
* ```make_dataset.py``` - склеивает два jsonl-файла в формате предыдущего скрипта и делает jsonl с вопросом и парой ответов - эталон и оцениваемый ответ
* ```evaluate.sh``` - передаёт файл с вопросом, эталонным и оцениваемым ответами в модель OpenAI с промптом - просьбой оценить ответ по шкале 1 - 0.8 - 0.5 - 0.0 и описать причину
* ```semantic-similarity.sh``` - считает косинусное расстояние между эмбеддингами эталонного и оцениваемого ответов, эмбеддинги строятся только локальной моделью

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
2026-10-02 12:57:29 | INFO     | started processing 3 new, changed or deleted wiki pages
2026-10-02 12:57:29 | INFO     | successfully uploaded 0 chunks from 0 new or changed wiki pages, 3 pages deleted, total collection size is 108

real    0m14.275s
user    0m6.690s
sys     0m3.005s

Building embeddings with OpenAI...
2026-10-02 12:57:40 | INFO     | started processing 3 new, changed or deleted wiki pages
2026-10-02 12:57:40 | INFO     | successfully uploaded 0 chunks from 0 new or changed wiki pages, 3 pages deleted, total collection size is 130

real    0m10.241s
user    0m8.463s
sys     0m1.321s
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
```

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

Модель OpenAI, неполная база:

```
./semantic-similarity.sh reference-openai-cut-vs-openai.jsonl | tee semantic-similarity-openai-cut-vs-openai.jsonl
```

Восстанавливаем базу:

```
mv /tmp/Слои\ Мрака.txt ../Task2/knowledge_base/
mv /tmp/Пакт.txt ../Task2/knowledge_base/
mv /tmp/Контроль.txt ../Task2/knowledge_base/
```

```
../Task3/index.sh

Building embeddings with local model...
2026-10-02 13:00:20 | INFO     | started processing 3 new, changed or deleted wiki pages
2026-10-02 13:00:40 | INFO     | successfully uploaded 9 chunks from 3 new or changed wiki pages, 0 pages deleted, total collection size is 117

real    0m36.342s
user    0m43.017s
sys     0m6.425s

Building embeddings with OpenAI...
2026-10-02 13:00:50 | INFO     | started processing 3 new, changed or deleted wiki pages
2026-10-02 13:00:53 | INFO     | successfully uploaded 12 chunks from 3 new or changed wiki pages, 0 pages deleted, total collection size is 142

real    0m14.315s
user    0m8.015s
sys     0m1.764s
```

### Анализ результатов

Ниже приведены таблицы оценки ответов с привлечением LLM OpenAI и с расстоянием между эмбеддинагми ответов. Косинусное расстояние между ответами OpenAI на полной и неполной базах считалось по эмбеддингам локальной можели, что немного не логично, но для иллюстрации подхода - приемлемо.

* local cut - локальная неполная база знаний vs OpenAI
* local - локальная полная база знаний vs OpenAI
* openai cut - OpenAI неполная база знаний vs OpenAI

| Question | LLM Score local cut | Cosine local cut | LLM Score local | Cosine local | LLM Score openai cut | Cosine openai cut |
|:--|--:|--:|--:|--:|--:|--:|
| Где произрастает красный бархат? | 0.0 | 0.476510 | 0.0 | 0.913955 | 0.8 | 0.734753 |
| Еcть ли какая-то третья сила, помимо Дневных и Ночных? | 0.8 | 0.168784 | 0.5 | 0.168784 | 1.0 | 0.841750 |
| Есть ли договорённости между Дневными и Ночными? | 0.0 | 0.461196 | 0.8 | 0.799081 | 0.0 | 0.530264 |
| Контролирует ли кто-то Дневных и Ночных? | 0.0 | 0.014892 | 0.8 | 0.680876 | 0.0 | 0.497660 |
| Кто такой Артём Молодецкий? | 0.5 | 0.786161 | 0.5 | 0.707452 | 1.0 | 0.933854 |
| Может ли обычный человек стать колдуном? | 0.5 | 0.901089 | 0.5 | 0.934531 | 0.8 | 0.906256 |
| Много ли произведений создал Демченко? | 0.5 | 0.720616 | 0.8 | 0.720616 | 0.8 | 0.944835 |
| Мультизвери - сильные колдуны? | 0.0 | 0.874725 | 0.0 | 0.868389 | 0.8 | 0.843535 |
| Ограничивает ли кто-то Дневных и Ночных в своих действиях? | 0.5 | 0.561152 | 0.0 | 0.194251 | 0.8 | 0.894293 |
| Сколько слоёв во мраке? | 1.0 | 0.608207 | 1.0 | 0.769937 | 1.0 | 0.825735 |

Видно, что:

* Локальная модель плохо отвечает на вопросы даже по полной базе знаний. Это может быть связано с ограничением самой модели, а может с тем, что при запросе к Qdrant в контекст локальной модели передаётся всего 3 вектора (хотя причина этого в свою очередь в том, что локальная модель путается на длинных контекстах). Например вопрос "Где произрастает красный бархат?":
  * OpenAI (эталон): "Красный бархат произрастает в Мраке, на его первом слое."
  * OpenAI (неполная база): "Красный бархат обитает только в Мраке."
  * local: "Красный бархат произрастает во втором слое Мрака." - фактическая ошибка даже на полной базе
  * local (неполная база): "Красный бархат живёт во всех мирах сразу. Он питается человеческими эмоциями (так же, как и Другие)." - фактическая ошибка
* Тот же самый вопрос про красный бархат выявляет несовершенство метрики семантической близости - для этого вопроса LLM score локальной модели равен нулю, а семантическая близость высокая, для полной базы вообще близка к единице. Для полной базы локальная модель использовала те же сущности - отсюда и высокая семантическая близость, но фактическая корректность пострадала.
* Ожидаемо упало качество (LLM score) ответов на вопросы, информация о которых удалена из базы знаний, так, и локальная модель и OpenAI неверно ответили на вопрос "Есть ли договорённости между Дневными и Ночными?", так как была удалена страница про Пакт.

Выводы:

* Метрика LLM-as-a-judge гораздо лучше метрики семантической близости и очень хорошо отражает качество ответа
* Метрика LLM-as-a-judge в "сыром" виде непригодна для кейса из задания т.к. требует передачи данных вовне. Возможно можно как-то обойти это ограничение заменяя чувствительные термины в эталонных и оцениваемых ответах, но вопрос как к этому отнесётся аудит остаётся открытым
* Без эксперта-человека обойтись сложно

### RAG и процесс оценки

Как примерно может выглядеть процесс оценки:

Сам RAG:

![RAG](/schemas/png/Task7/RAG%20Query%20Sequence.png)

Оценка:

![Evaluation](/schemas/png/Task7/RAG%20Evaluation%20Sequence.png)

