# razgony_bot
Бот отслеживает выпуски разгонов и присылает подписавшимся ссыку на новый выпуск

ТЗ:
Планировщик задач запускает по очереди два метода:
парсер свежатины в бд и рассылатель свежатины в тг.

в бд одна таблица:
id pk,
урл видеоролика (можно просто айди видеоролика),
пометка (булево) отправлено или не отправлено

Ютуб инвертирует порядок роликов, поэтому при заполнении базы парсером нужно инвертировать спарсенный список, (самый старый 131 выпуск должен добавиться с 131 айдишником).

Если делать так:
1. парсер парсит список всех роликов в плэйлисте
2. список инвертируется
3. итерируемся по списку и каждую запись сразу пытаемся вставить в базу методом инсерт ор игнор.
то будет долго.

================= это вариант, когда присылается сразу весь плейлист ================
Айдишники в базе совпадают с номерами выпусков (чисто случайно)
Поэтому можно сделать быстрый вариант:
1. парсер парсит список всех роликов в плэйлисте (от этого не уйти)
2. перед добавлением в бд, список обязательно инвертируем, получая 1 ролик под 1 номером, соответственно 1 айди в базе
3. получаем из базы айдишник последней записи
4. добавляем в базу из спарсенного списка все ссылки, которые в спарсенном списке после последнего айдишника из базы, ставим метку new
5. второй метод из задачи шедулера собирает все записи с меткой new и отправляет пользователю бота (выдерживать паузу между отправкой сообщений)

================ вариант с проверкой даты. высылаются только те ролики, которые появились ПОСЛЕ подписки ============
1. создать в бд поле с датой, парсить дату релиза ролика
2. -//-
3. -//-
4. -//-
5. второй метод из задачи шедулера собирает все записи с меткой new, КОТОРЫЕ имеют дату >= даты подписки и отправляет пользователю бота (выдерживать паузу между отправкой сообщений)
6. следовательно нужно завести таблицу пользователей (1 пользователь - Многие плэйлисты):
один (users)
- tg_id INTEGER NOT NULL UNIQUE (добавить, что при конфликте пропускаем, не помню синтаксис сейчас) !!!ВАЖНО. в субд sqlite3 интежер не должен превышать 19 байт
многие (playlists)
- playlist_url TEXT UNIQUE (тут при задвоении надо назначить существующую позицию)
- user INTEGER
- is_new INTEGER (булево значение, по умолчанию 1 (True), если True - этот список мы еще не парсили)
- FOREIGN KEY (user) REFERENCES users(tg_user_id)
у каждого пользователя несколько плейлистов
многие (videos)
- video_url TEXT UNIQUE (тут при задвоении надо назначить существующую позицию)
- playlist_url TEXT
- is_new INTEGER (булево значение, по умолчанию 1 (True), если True - это видео мы еще не отправляли)
- FOREIGN KEY (playlist) REFERENCES playlists(playlist)
у каждого плейлиста несколько видеороликов
----------------------------------ИТОГО:
0. пользователь бота прислал ссылку на плейлист, который он хочет отслеживать.
1. айди этого пользователя добавляется (или игнорится) в таблицу пользователей,
айди присланной ссылки на плейлист добавляется (или игнорится в таблицу плейлистов),
ссылка связывается с пользователем (много ссылок, один пользователь), так же (по умолчанию средствами синтаксиса sql) выставляется метка is_new = True
2. по таймеру запускается парсер, который выбирает все айдишники плейлистов с пометкой is_new и парсит:
парсер на вход принимает айдишник плейлиста (PLcQngyvNgfmK0mOFKfVdi2RNiaJTfuL5e), подставляет префикс (https://www.youtube.com/playlist?list=), получает данные видео: дата релиза, тайтл, айдишник и сохраняет в таблицу youtube_videos.
СВЯЗИ:
user m2m video
user m2m playlist
video m2m playlist
!перед добавлением инвертируем список!
3. в этой же задаче таймера следующим методом рассылаем пользователям их данные:
выбираем пользователей и видеоролики с пометкой new
отправляем каждому пользователю свой видеоролик