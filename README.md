# ConstellixManager

Проект предназначен для ускорения работы с сервисом Constellix.


Доступный функционал на данный момент:
* -создание доменов с указанным именем и А записью;
* -изменение А записей доменов для ускорения миграции;
* -удаление домена;
* -зануление домена (A_record = 127.0.0.1);
* -локальный аналог БД, помогает быстрее формировать запросы;
* -cохранение поcле инициализации в исполняемой директории файла 'not_found.txt'
  - в нем будут находиться все домены не найденые в DNS сервисе Constellix.


**1)** Для начала следует установить все необходимые модули:
`pip3 install -r requirements.txt`

**1.1)** Юзабельно для просмотра опций:
`python3 actions.py -h`


**2)** Создание доменов и А записей к ним:
`python3 actions.py create domains.txt`

<a href="https://ibb.co/SPgQhXd"><img src="https://i.ibb.co/g38v5MP/Create-domains-with-record.png" alt="Create-domains-with-record" border="0" /></a>

**3)** Миграция доменов:
`python3 actions.py update domains.txt`

<a href="https://ibb.co/4F7N8vM"><img src="https://i.ibb.co/XWbJ70p/Update-domain-record.png" alt="Update-domain-record" border="0"></a>

**4)** Удалениe доменов:
`python3 actions.py delete domains.txt`

<a href="https://ibb.co/W64SgTB"><img src="https://i.ibb.co/1LtH8SR/Delete-domains.png" alt="Delete-domains" border="0"></a>

**5)** Зануление доменов:
`python3 actions.py localhost domains.txt`

<a href="https://ibb.co/Q6KxcB3"><img src="https://i.ibb.co/K9r8GZp/Set-A-record-to-localhost.png" alt="Set-A-record-to-localhost" border="0"></a>