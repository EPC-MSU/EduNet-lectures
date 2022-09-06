# MSU.AI

Репозиторий проекта **[Искусственный интеллект и наука МГУ имени М.В. Ломоносова](https://msu.ai)**

Курс: **[Нейронные сети и их применение в научных исследованиях](https://msu.ai/nn_for_scientists)**

Здесь разрабатываются блокноты jupyter, по которым читается курс. Наиболее актуальные блокноты доступны в верхушке дефолтной ветви репозитория. Все изображения и другие медиаресурсы блокнотов хранятся отдельно на веб сервере и попадают в блокноты через гиперссылки. Рекомендуемая среда для запуска блокнотов - [Google Colab](https://colab.research.google.com). **Блокноты нужно сначала запускать** на полное выполнение (Run all), а затем читать, так как часть иллюстраций генерируется кодом. Блокноты с заданиями не публикуются.

## СС0 - лицензия публичного достояния

Весь разработанный **курс передан в публичное достояние**. Тексты, коды - написаны нами. Изображения по большей части нарисованы нами и тоже распространяются **вместе с исходниками** под лицензией CC0. Все остальные изображения это ссылки на чужой результат, который не требует перерисовки и мы ссылаемся на автора в тексте блокнота. Датасеты, тем более, по большей части заимствованные и тоже содержат ссылки на источник.

**Зачем это сделано?** Для того, чтобы без оглядки на юристов, можно было на основе наших материалов создать свой учебный курс, полностью скопировать наш, создать свой коммерческий продукт и продавать его, и т.д. Иными словами - заниматься конструктивной деятельностью и не беспокоиться об ограничениях. Это подарок человечеству во имя всеобщего процветания.

**Что позволило это сделать?** Мы работаем при поддержке некоммерческого фонда развития науки и образования [«Интеллект»](https://intellect-foundation.ru/). Мы не ставим целью продажу курса, поэтому наработанные материалы не нужно прятать от потенциальных покупателей. Наши цели это повышение качества науки в МГУ. Максимально открытая лицензия этому не противоречит.

## Как пользоваться

В папке `out` находятся сами блокноты. Они разбиты по лекциям. План занятий выделен в файл `Curriculum.md` и он автогенерируется на основе заголовков H1 и H2 в блокнотах.

Для использования нужно иметь аккаунт в Google. Зайти в [Google Colab](https://colab.research.google.com). Выбрать там загрузку файла блокнота (Upload). Загрузить любой файл блокнота лекции - например `L07_Batch_normalization.ipynb`. В меню `Runtime` выбрать `Change runtime type` и вместо None поставить GPU. Затем там же нажать `Run all` и подождать выполнения блокнота до конца. Мы следим за тем, что блокноты должны выполнятся от начала до конца без остановок, а также за тем, чтобы время выполнения блокнота было не больше 20 минут (на Google Colab Pro).

**Profit!**

### Возможные проблемы

- **Не грузятся картинки**. Это может быть по нашей вине, а может вы выбрали не ту ветвь. Проверьте, что файл лекции выгружен с верхушки дефолтной ветви. Обычно мы поддерживаем одновременно несколько ветвей, но бывают разные сбои, даже с применением автоматики.
- **Не работает код**. Причиной чаще всего являются изменения в версиях библиотек в  [Google Colab](https://colab.research.google.com). Иногда разработчик библиотек меняет правила пользования без периода предупреждения. Причиной также может быть недоступность внешнего ресурса (не скачивается датасет). Мы кэшируем датасеты на своём сервере, чтобы от этого защититься. Два раза в год мы проверяем, что код работает без сбоев и исправляем его, а также внешние зависимости, если видим ошибку.

Будем признательны, если вы сообщите об обнаруженных проблемах через Issue. Мы тратим силы на проверки, чтобы наши материалы работали у всех, так что информация о сбоях важна для нас.

### Я особенный

Все блокноты должны запускаться и локально, с помощью jupyter notebook, но мы это не проверяем. Нужные пакеты мы выписывали в `requirements.txt`.

```
pip install -r requirements.txt
```
Также, предположительно, блокноты можно запускать в [**DataSphere**](https://u.habr.com/yds_service) от Яндекса.

## Как разрабатывать

В папке `hooks` находятся хуки для чистки блокнотов перед коммитом. Это важный автоматический инструмент, чтобы блокнот не прорастал метаданными, которые там остаются даже после команды `Clear all outputs`. Этим особенно страдает Colab, в котором как раз удобно редактировать файлы блокнотов. Хук запускает скрипт очистки блокнота от метаданных `cleaner.py`. Скрипт можно запускать и вручную, но это неудобно.

`autotc.py` нужен для построения файла `Curriculum.md`, содержащего программу занятий. Таким образом, программа занятий всегда соответствует заголовкам блокнота.

`autolinks.py` нужен для автоматизированной проверки внешних ссылок.

### Workflow

Разработка ведётся с использованием `ticket-branch`. Номер `ticket-branch` привязан к внутренней системе треккинга задач. Именование главных ветвей двухциферное (например dev-1.7). Ведётся несколько таких ветвей, где наиболее старые это legacy, затем есть дефолтная ветвь, являющаяся стабильной, и ветвь для новых нестабильных доработок для следующего набора на курс.

### Нейминг

Кириллица в названиях недопустима, вместо пробелов - нижние подчеркивания, префикс - L для обозначения лекции, нумерация из двух цифр, далее - тема лекции.
Первая буква темы лекции заглавная, остальные строчные.

#### Подробнее о cleaner.py
* Скрипт `cleaner.py` очищает метаданные (чтобы блокноты не весили десятки МБ), выводит предупреждения о ссылках на локальные изображения или изображения вставленные в бинарном виде.
* Запускать можно из консоли с аргументами (аргументы смотрите через `-h`) либо настроить гит-хук, который автоматически будет его запускать во время коммита.
* Настройка хуков:
  * Копировать папку `hooks` внутрь папки `.git` слиянием/заменой (.git может быть скрыта в системе)
  * Если у вас Linux/Mac могут возникнуть проблемы с правами файла, поэтому нужно дать доступ:
    * (Linux/Mac) В терминале: `chmod +x .git/hooks/pre-commit` и `chmod +x .git/hooks/pre-merge-commit`
      * (Mac) Иногда нужно дополнительно вызвать: `xattr -d com.apple.quarantine .git/hooks/pre-commit` и `xattr -d com.apple.quarantine .git/hooks/pre-merge-commit`
  * При нажатии на кнопку коммит, скрипт автоматически запустится и в локальную ветвь попадут уже почищенные блокноты.
  * В smartgit до нажатия кнопки коммита изменения не видны. После нажатия, перед пушем их можно увидеть в локальной ветке.
  * Не забыть сделать всё то же самое для репозитория secret
