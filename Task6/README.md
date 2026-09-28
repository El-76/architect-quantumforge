## Модельный скрипт

Модельный скрипт смотрит в каталог, детектирует изменения, считая хеши и храня их в отдельном файле, и записывает вектора в Qdrant.

Обновляться будет только БД локальной модели (для обновления OpenAI нужно повторить те же шаги, модифицировав upload.sh , ключи см. в Задании 3).

Здесь и далее предполагается, что установлен pyenv и в нём установлен python 3.11.16 (см. README всего проекта).

Также предполагается, что запущен Qdrant (см. Задание 3).

Чистим локальную коллекцию:

```
curl -X DELETE http://localhost:6333/collections/wiki-local | jq .
```

"Устанавливаем" скрипты:

```
sudo mkdir -p /opt/practicum7/bin

sudo chown $(id -u):$(id -g) -R /opt/practicum7

cp upload.sh /opt/practicum7/bin/

cd /opt/practicum7/bin/

pyenv local 3.11.16

cd -

cp ../Task3/index_or_query.py /opt/practicum7/bin/

sudo mkdir -p /var/lib/practicum7/hashes

sudo chown $(id -u):$(id -g) -R /var/lib/practicum7

sudo mkdir -p /var/log/practicum7

sudo chown $(id -u):$(id -g) -R /var/log/practicum7

sudo mkdir -p /var/run/practicum7

sudo chown $(id -u):$(id -g) -R /var/run/practicum7
```

Копируем wiki:

```
cp -r ../Task2/knowledge_base /var/lib/practicum7/
```

"Откладываем в сторону" один файл:

```
mv /var/lib/practicum7/knowledge_base/Сёку.txt /tmp/
```

Настраиваем cron:

```
crontab -e

* * * * * /opt/practicum7/bin/upload.sh
```

Смотрим log (через несколько минут, примерно 4 минуты на моём ноутбуке):

```
cat /var/log/practicum7/upload.log

2026-09-27 22:44:15 | INFO     | started processing 86 new or changed wiki pages
2026-09-27 22:47:13 | INFO     | successfully uploaded 116 chunks from 86 new or changed wiki pages, total collection size is 116
```

Смотрим размер коллекции:

```
curl -s -X POST http://localhost:6333/collections/wiki-local/points/count   -H 'Content-Type: application/json'   -d '{
    "exact": true
  }' | jq .result.count
116
```

Смотрим содержимое документов с ID 9 и 86:

```
curl -s -X POST 'http://localhost:6333/collections/wiki-local/points/scroll' -H 'Content-Type: application/json' -d '{
    "filter": {
      "must": [
        {
          "key": "page_id",
          "match": {
            "any": [9, 86]
          }
        }
      ]
    },
    "with_payload": true,
    "with_vector": false
  }' | jq .
```

Документ 9 отсутствует, в документе 86 слово "способен":

```
{
  "result": {
    "points": [
      {
        "id": 86001,
        "payload": {
          "page_id": 86,
          "title": "Мышь",
          "chunk_id": 1,
          "page_content": "Title: Мышь\nБоевой колдун-калейдоскоп, способен превращаться в мышей различных пород. Друг и постоянный напарник Хомячка. По слухам был Ночным Другим."
        }
      }
    ],
    "next_page_offset": null
  },
  "status": "ok",
  "time": 0.01309133
}
```

Смотрим ещё через минуту:

```
cat /var/log/practicum7/upload.log

2026-09-27 22:48:16 | INFO     | nothing to upload
```

\- загружать нечего.

Возвращаем отложенный файл и меняем другой:

```
mv /tmp/Сёку.txt /var/lib/practicum7/knowledge_base/Сёку.txt

sed -i s/способен/способный/g /var/lib/practicum7/knowledge_base/Мышь.txt
```

Ждём и смотрим в лог:

```
cat /var/log/practicum7/upload.log

2026-09-27 22:56:16 | INFO     | started processing 2 new or changed wiki pages
2026-09-27 22:56:17 | INFO     | successfully uploaded 2 chunks from 2 new or changed wiki pages, total collection size is 117
```

Смотрим размер коллекции:

```
curl -s -X POST http://localhost:6333/collections/wiki-local/points/count   -H 'Content-Type: application/json'   -d '{
    "exact": true
  }' | jq .result.count
116
```

\- добавился 1 документ.

Смотрим содержимое документов с ID 9 и 86:

```
curl -s -X POST 'http://localhost:6333/collections/wiki-local/points/scroll' -H 'Content-Type: application/json' -d '{
    "filter": {
      "must": [
        {
          "key": "page_id",
          "match": {
            "any": [9, 86]
          }
        }
      ]
    },
    "with_payload": true,
    "with_vector": false
  }' | jq .
```

Документ 9 появился, в документе 86 слово "способный":

```
{
  "result": {
    "points": [
      {
        "id": 9001,
        "payload": {
          "page_id": 9,
          "title": "Сёку",
          "chunk_id": 1,
          "page_content": "Title: Сёку\nон же \"Прокурор Ушедших\", он же \"Чернота Ночи\" Великий Ночной колдун, давно отошедший от дел и живущий жизнью обычного Другого в Мехико. Упоминается в книге \"Взгляд Тёмной Атлантиды\"."
        }
      },
      {
        "id": 86001,
        "payload": {
          "page_id": 86,
          "title": "Мышь",
          "chunk_id": 1,
          "page_content": "Title: Мышь\nБоевой колдун-калейдоскоп, способный превращаться в мышей различных пород. Друг и постоянный напарник Хомячка. По слухам был Ночным Другим."
        }
      }
    ],
    "next_page_offset": null
  },
  "status": "ok",
  "time": 0.002857589
}
```

## Диаграммы.

Диаграмма контейнеров разработана с учётом двух источников - Confluence и Google Drive.

На диаграмме компонентов показан только экспорт из Google Drive.

Идея такая же, как в модельном скрипте - считаем хеши, изменённые файлы пишем в Qdrant.

Всё запускается на том же хосте из Задания 1.

Логи пишутся локально, в задании ничего нет про ELK и тп, потом можно их перенаправить через filebeat.

### Диаграмма контейнеров

![Диаграмма контейнеров](../schemas/png/Task6/Container.png)

### Диаграмма компонент

![Диаграмма компонент](../schemas/png/Task6/Component.png)
