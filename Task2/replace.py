import nltk
from nltk.stem.snowball import RussianStemmer
import pymorphy3
import sys

stemmer = RussianStemmer()
morph = pymorphy3.MorphAnalyzer()

def get_same_form(source_word, target_word):
    source_parses = morph.parse(source_word)
 
    if not source_parses:
        return None

    for match_all in [ True, False ]:
        for source_parse in source_parses:
            source_tag = source_parse.tag

            if match_all:
                source_grammemes = source_tag.grammemes
            else:
                source_grammemes = set()

                if source_tag.number:
                    source_grammemes.add(source_tag.number)

                if source_tag.case:
                    source_grammemes.add(source_tag.case)
 
        target_parses = morph.parse(target_word)

        for parse in target_parses:
            if parse.tag.POS == source_tag.POS:
                reduced = parse.inflect(source_grammemes)

                if reduced:
                    return reduced.word
 
    return None

replacements = {
    'Тёмный': 'Ночной',
    'Светлый': 'Дневной',
    'Инициированный': 'Вдохновлённый',
    'Лайк': 'Восторг',
    'Шереметьев': 'Призоров',
    'Киссель': 'Портвин',
    'Алиса': 'Лариса',
    'Донникова': 'Конникова',
    'Алита': 'Гелла',
    'Алишер': 'Ильдар',
    'Ганиев': 'Алиев',
    'Тюнников': 'Лунников',
    'Анна': 'Агнесса',
    'Тихоновна': 'Леонидовна',
    'Лемешева': 'Карбышева',
    'Антон': 'Артём',
    'Городецкий': 'Молодецкий',
    'Арина': 'Ирина',
    'Артефакты': 'Предметы',
    'амулеты': 'талисманы',
    'Аура': 'Сияние',
    'Белое': 'Серебряное',
    'марево': 'зарево',
#    'Бессмертие': 'Бессмертие',
    'Братья': 'Сёстры',
    'Регин': 'Балин',
    'Вампир': 'Упырь',
    'Витезслав': 'Святослав',
    'Грубин': 'Чёрствый',
    'Галина': 'Полина',
    'Добронравова': 'Великодушная',
    'Гарик': 'Артур',
    'Геннадий': 'Аркадий',
    'Гесер': 'Донер',
    'Борис': 'Павел',
    'Игнатьевич': 'Олегович',
    'Гэллемар': 'Абрахас',
    'Данила': 'Михаил',
    'Двуединый': 'Янус',
    'Денис': 'Сергей',
    'Дневной': 'Белый',
    'Дозор': 'Патруль',
    'Договор': 'Пакт',
    'Егор': 'Дмитрий',
    'Завулон': 'Астарот',
#    'Заглавная страница': 'Заглавная страница',
    'Заклинания': 'Мантры',
    'Зеркало': 'Отражение',
    'Игнат': 'Панкрат',
    'Игорь': 'Иван',
    'Теплов': 'Холодов',
    'Изначальные': 'Первородные',
    'Силы': 'Энергии',
    'Илья': 'Даниил',
    'Инициация': 'Вдохновение',
    'Инквизиция': 'Контроль',
    'Инкуб': 'Самаэль',
    'Саушкин': 'Матушкин',
    'Костя': 'Юра',
    'Лас': 'Бес',
    'Лукьяненко': 'Демченко',
    'Васильевич': 'Петрович',
    'Людвиг': 'Фредерик',
    'Иероним': 'Иларион',
    'Кюхбауэр': 'Босх',
    'Маг': 'Колдун',
    'перевёртыш': 'калейдоскоп',
    'Максим': 'Эрик',
    'Марк': 'Арнольд',
    'Эммануилович': 'Самуилович',
    'Жермензон': 'Либерзон',
    'Медведь': 'Мышь',
    'Надя': 'Галя',
    'Николай': 'Евгений',
    'Ночной': 'Чёрный',
    'Самарканд': 'Буенос-Айрес',
    'Санкт-Петербург': 'Лас-Вегас',
    'Оборотень': 'Мультизверь',
    'Ольга': 'Елена',
    'Превращение': 'Трансформация',
    'Иной': 'Другой',
    'Развоплощение': 'Дезынтеграция',
    'Реморализация': 'Перевоспитание',
    'Рустам': 'Руслан',
    'Саркофаг': 'Надгробие',
    'Свет': 'День',
    'Светлана': 'Мария',
    'Семён': 'Потап',
    'Павлович': 'Сергеевич',
    'Колобов': 'Хлебников',
    'Сергей': 'Александр',
    'Глыба': 'Скала',
    'молебен': 'ритуал',
    'Суккуб': 'Лилит',
    'Сумрак': 'Мрак',
    'Тигр': 'Хомяк',
    'Тигрёнок': 'Хомячок',
    'Тимур': 'Захар',
    'Борисович': 'Алексеевич',
    'Равенбах': 'Авербух',
    'Толик': 'Эдик',
    'Томас': 'Джефф',
    'Лермонт': 'Свифт',
    'Тьма': 'Ночь',
    'Фарид': 'Фарух',
    'Хена': 'Вона',
    'Шагрон': 'Патрон',
    'Шиндже': 'Сёку',
    'Шухарты': 'Отарки',
    'Эдгар': 'Алан',
    'Юрий': 'Андрей',
}

replacement_stems = {}

for replacement in replacements:
    replacement_stems[stemmer.stem(replacement)] = replacements[replacement]

text = sys.stdin.read()

tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
tokens = tokenizer.tokenize(text.replace("\n", "\nLF\n").replace(".", " DOT ").replace(",", " COMMA ").replace("-", " DASH "))

first = True
for token in tokens:
    is_title = token.istitle()

    stem = stemmer.stem(token)

    replacement = replacement_stems.get(stem, None)

    if replacement is not None:
        replacement_token = get_same_form(token, replacement)

        if replacement_token is not None:
            token = replacement_token

    if first:
        first = False
    elif token != "DOT" and token != "COMMA" and token != "DASH":
        print(' ', end="")

    if token == "LF":
        first = True
        print()
    elif token == "DOT":
        print('.', end="")
    elif token == "COMMA":
        print(',', end="")
    elif token == 'DASH':
        first = True
        print('-', end='')
    else:
        print(f'{token.capitalize() if is_title else token}', end="")


