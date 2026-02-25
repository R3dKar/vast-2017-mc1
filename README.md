# Scenario
## Overview

Mistford is a mid-size city located to the southwest of a large nature preserve. The city has a small industrial area with four light-manufacturing endeavors. Mitch Vogel is a post-doc student studying ornithology at Mistford College and has been discovering signs that the number of nesting pairs of the Rose-Crested Blue Pipit, a popular local bird due to its attractive plumage and pleasant songs, is decreasing! The decrease is sufficiently significant that the Pangera Ornithology Conservation Society is sponsoring Mitch to undertake additional studies to identify the possible reasons. Mitch is gaining access to several datasets that may help him in his work, and he has asked you (and your colleagues) as experts in visual analytics to help him analyze these datasets.
* Мистфорд - город среднего размера, расположенный к юго-западу от крупного природного заповедника. В городе есть небольшая промышленная зона с четырьмя предприятиями легкой промышленности. Митч Фогель, аспирант, изучающий орнитологию в Мистфордском колледже, обнаружил признаки того, что количество гнездящихся пар розовохохлой синей свиристели, популярной местной птицы из-за ее привлекательного оперения и приятных песен, сокращается! Это снижение настолько значительно, что Общество охраны орнитологии Пангеры спонсирует Митча для проведения дополнительных исследований с целью выявления возможных причин. Митч получает доступ к нескольким наборам данных, которые могут помочь ему в его работе, и он попросил вас (и ваших коллег) как экспертов в области визуальной аналитики помочь ему проанализировать эти наборы данных.

## Mini-Challenge 1

The Boonsong Lekagul Nature Preserve is used by local residents and tourists for day-trips, overnight camping or sometimes just passing through to access main thoroughfares on the opposite sides of the preserve. The entrance booths of the preserve are monitored in order to generate revenue as well as monitor usage. Vehicles entering and exiting the preserve must pay a fee based on the number of axles (personal auto, recreational trailer, semi-trailer, etc.). This generates a data stream with entry/exit timestamps and vehicle type. There are also other locations in the Preserve that register traffic passing through. While hiking through the various parts of the Preserve, Mitch has noticed some odd behaviors of vehicles that he doesn’t think are consistent with the kinds of park visitors he would expect. If there were some way that Mitch could analyze the behaviors of vehicles through the park over time, it may assist him in his investigations.
* Природный заповедник Бунсонг Лекагул используется местными жителями и туристами для однодневных поездок, ночевок в кемпингах, а иногда и просто для проезда через него, чтобы добраться до основных магистралей на противоположных сторонах заповедника. Контроль за въездными билетами в заповедник осуществляется с целью получения дохода, а также контроля за использованием. Транспортные средства, въезжающие в заповедник и выезжающие из него, должны оплачивать сбор в зависимости от количества осей (личный автомобиль, прогулочный прицеп, полуприцеп и т.д.). При этом генерируется поток данных с отметками времени въезда/выезда и типом транспортного средства. В заповеднике есть и другие места, где регистрируется движение транспорта. Прогуливаясь по различным частям заповедника, Митч заметил некоторые странности в поведении транспортных средств, которые, по его мнению, не соответствуют ожиданиям посетителей парка. Если бы Митч мог каким-то образом анализировать поведение транспортных средств в парке с течением времени, это могло бы помочь ему в его расследованиях.

# Questions

1. “Patterns of Life” analyses depend on recognizing repeating patterns of activities by individuals or groups. Describe up to six daily patterns of life by vehicles traveling through and within the park. Characterize the patterns by describing the kinds of vehicles participating, their spatial activities (where do they go?), their temporal activities (when does the pattern happen?), and provide a hypothesis of what the pattern represents (for example, if I drove to a coffee house every morning, but did not stay for long, you might hypothesize I’m getting coffee “to-go”). Please limit your answer to six images and 500 words.
    * Анализ “Моделей жизни” основан на распознавании повторяющихся моделей деятельности отдельных лиц или групп. Опишите до шести ежедневных моделей жизни транспортных средств, проезжающих по парку и в его пределах. Охарактеризуйте паттерны, описав типы участвующих в них транспортных средств, их пространственную активность (куда они направляются?), их временную активность (когда проявляется паттерн?) и выдвиньте гипотезу о том, что представляет собой паттерн (например, если бы я каждое утро ездил в кофейню, но не сделал этого. если я останусь надолго, вы можете предположить, что я выпью кофе “на скорую руку”). Пожалуйста, ограничьте свой ответ шестью изображениями и 500 словами.

2. Patterns of Life analyses may also depend on understanding what patterns appear over longer periods of time (in this case, over multiple days). Describe up to six patterns of life that occur over multiple days (including across the entire data set) by vehicles traveling through and within the park. Characterize the patterns by describing the kinds of vehicles participating, their spatial activities (where do they go?), their temporal activities (when does the pattern happen?), and provide a hypothesis of what the pattern represents (for example, many vehicles showing up at the same location each Saturday at the same time may suggest some activity occurring there each Saturday). Please limit your answer to six images and 500 words.
    * Анализ закономерностей жизнедеятельности может также зависеть от понимания того, какие закономерности проявляются в течение более длительных периодов времени (в данном случае, в течение нескольких дней). Опишите до шести закономерностей жизнедеятельности, которые наблюдаются в течение нескольких дней (включая весь набор данных) у транспортных средств, проезжающих через парк и в пределах парка. Охарактеризуйте закономерности, описав типы участвующих транспортных средств, их пространственную активность (куда они направляются?), их временную активность (когда возникает закономерность?) и выдвиньте гипотезу о том, что представляет собой эта закономерность (например, многие транспортные средства появляются в одном и том же месте каждую субботу в одно и то же время. время может указывать на то, что каждую субботу там происходит какое-то мероприятие). Пожалуйста, ограничьте свой ответ шестью изображениями и 500 словами.

3. Unusual patterns may be patterns of activity that changes from an established pattern, or are just difficult to explain from what you know of a situation. Describe up to six unusual patterns (either single day or multiple days) and highlight why you find them unusual. Please limit your answer to six images and 500 words.
    * Необычными могут быть модели поведения, которые отличаются от устоявшихся или которые просто трудно объяснить на основе того, что вы знаете о ситуации. Опишите до шести необычных моделей поведения (как за один день, так и за несколько дней) и укажите, почему они кажутся вам необычными. Пожалуйста, ограничьте свой ответ шестью изображениями и 500 словами.

4. What are the top 3 patterns you discovered that you suspect could be most impactful to bird life in the nature preserve? (Provide a short text answer.)
    * Назовите 3 основные закономерности, которые, по вашему мнению, могут оказать наибольшее влияние на жизнь птиц в заповеднике? (Ответьте коротким текстом).

# Additional Reviewer Considerations

MC1 Questions and Approach:
* Was the submission able to sort out suspicious patterns (relevant to the scenario) from the false leads (which would not present a feasible threat to wildlife)? Were multiple variations in patterns identified?
* If there were hypotheses that remained unresolved, did the submission specify actions to be taken to resolve them?


MC1 Application of visual analytics:
* Did the team develop an innovative visual analytic tool? Alternatively, did they use an existing tool in an innovative way?
* Did visualizations enable the analysis process? Or did they merely illustrate conclusions? Did the submission rely more heavily on non-visual analytic approaches?
* Did their tool allow useful interactions?
* Did they use all the available data?
* Was the submission clear?

-----
Вопросы и подход MC1:
* Удалось ли в ходе рассмотрения заявки отделить подозрительные закономерности (соответствующие сценарию) от ложных выводов (которые не представляли бы реальной угрозы для дикой природы)? Были ли выявлены многочисленные вариации в закономерностях?
* Если были какие-то гипотезы, которые остались нерешенными, были ли в заявке указаны действия, которые необходимо предпринять для их решения?


Применение визуальной аналитики в MC1:
* Разработала ли команда инновационный инструмент визуальной аналитики? В качестве альтернативы, они использовали существующий инструмент инновационным образом?
* Способствовали ли визуализации процессу анализа? Или они просто иллюстрировали выводы? Опирались ли материалы в большей степени на невизуальные аналитические подходы?
* Обеспечивал ли их инструментарий полезные взаимодействия?
* Использовали ли они все доступные данные?
* Была ли информация понятной?
