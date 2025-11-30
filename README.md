# NormaText
Десктопное приложение на Python для проверки .docx-документов на соответствие **ГОСТ Р 7.0.97-2016**.

## Назначение
NormaText помогает студентам, инженерам и техническим специалистам:
- проверять структуру документа,
- выявлять недопустимую терминологию,
- находить ошибки в нумерации,
- автоматически исправлять простые нарушения.

## Технологии
- Язык: **Python 3.14**
- GUI: **tkinter**
- Работа с .docx: **python-docx**
- Морфологический анализ: **pymorphy3**
- Автономность: **без интернета и внешних API**

## Тестирование
Тесты проверяют:
- корректность лемматизации(pymorphy3)
- определение запрещенных слов 
- игнорирование неккоректных входных данных

## UML-Диаграммы

### Use case diagram
![Use Case Diagram](https://raw.githubusercontent.com/phio69/NormaText/main/images/usecasediagram.png)

### Class Diagram
![Class Diagram](https://raw.githubusercontent.com/phio69/NormaText/main/images/classdiagram.png)