import requests
from lxml import html
from datetime import date, datetime


async def correct_mark(mark):
    if len(mark) > 1:
        if mark[1] == "-":
            new_mark = f"{int(mark[0]) - 1}.75"
            return new_mark
        if mark[1] == "+":
            new_mark = f"{int(mark[0])}.50"
            return new_mark
    else:
        return mark


async def get_day(string):
    day = ""
    for i in string:
        try:
            int(i)
            day += i
        except ValueError:
            break
    return int(day)


async def get_classroom(tail):
    tail = tail.strip()
    i = len(tail) - 1
    room = []
    while i > 0:
        if tail[i] == "(":
            room.insert(0, tail[i])
            break
        else:
            room.insert(0, tail[i])
        i -= 1
    return "".join(room)


async def get_teacher(tail):
    tail = tail.strip()
    i = len(tail) - 1
    teacher = []
    after_room = False
    while i > 0:
        if after_room:
            if tail[i] == "-":
                break
            else:
                teacher.insert(0, tail[i])
        if tail[i] == "(":
            after_room = True
        i -= 1
    return "".join(teacher).strip()


async def remove_spaces(tab):
    i = 0
    while i < len(tab):
        if tab[i].strip() == "":
            del tab[i]
        else:
            tab[i] = tab[i].strip()
            i += 1
    return tab


async def get_last_marks(mobi, data, web_url):
    try:
        web = requests.post(
            f"https://{web_url}.mobidziennik.pl/mobile/glowna", data=data
        )
        tree = html.fromstring(web.content)
        root = tree.xpath('//td[@class="page-dz-home-hist-cnt"]/../..')
        for i in root:
            for y in i:
                if y.get("class") == "rowRolling":
                    y = (
                        y.getchildren()[0]
                        .getchildren()[0]
                        .getchildren()[0]
                        .getchildren()
                    )
                    for z in y:
                        z = z.getchildren()[0]
                        if (
                            z.text == "Grupa:"
                            or z.text == "Rodzaj:"
                            or z.text == "Treść:"
                        ):
                            mobi.description.append(z.tail)
                else:
                    y = y.getchildren()[1:]
                    for z in y:
                        if z.get("class") == "page-dz-home-hist-cnt":
                            mobi.last_marks_name.append(z.text)
                        else:
                            mobi.last_marks.append(z.text)
        mobi.last_marks = mobi.last_marks[:3]
        mobi.last_marks_name = mobi.last_marks_name[:3]
        mobi.description = mobi.description[:3]
        mobi.last_marks = await remove_spaces(mobi.last_marks)
        mobi.last_marks_name = await remove_spaces(mobi.last_marks_name)
    except:
        pass


async def get_first_marks(mobi, data, web_url):
    web = requests.post(
        f"https://{web_url}.mobidziennik.pl/mobile/oceny?semestr=1", data=data
    )
    tree = html.fromstring(web.content)
    root = tree.xpath('//tr[@class="subject"]/td')
    for i in root:
        try:
            i = float(i.text.strip())
        except ValueError:
            if i.text.strip() != "":
                mobi.marks_avg_name.append(i.text)
                mobi.marks_avg.append(i.getparent().getchildren()[2].text.strip())
    mobi.marks_avg_name = await remove_spaces(mobi.marks_avg_name)

    web = requests.post(
        f"https://{web_url}.mobidziennik.pl/mobile/oceny?semestr=1&koncowe", data=data
    )
    tree = html.fromstring(web.content)
    root = tree.xpath('//span[@class="color-red"]/../..')
    for i in root:
        i = i.getchildren()
        if i[0].text.strip() != "Śródroczna":
            mobi.red_names.append(i[0].getchildren()[0].tail.strip())
            mobi.red_marks.append(i[1].getchildren()[0].text.strip())

    avg_counter = 0
    for i in range(len(mobi.marks_avg)):
        if mobi.marks_avg[i] != "":
            try:
                index = mobi.red_names.index(mobi.marks_avg_name[i])
                przedmiot = mobi.red_marks[index]
                przedmiot = await correct_mark(przedmiot)
            except ValueError:
                przedmiot = mobi.marks_avg[i]
            try:
                przedmiot = float(przedmiot)
                mobi.avg += float(przedmiot)
                avg_counter += 1
            except ValueError:
                pass
    if avg_counter > 0:
        mobi.avg = str(mobi.avg / avg_counter)[:4]
    else:
        mobi.avg = ""


async def get_second_marks(mobi, data, web_url):
    web = requests.post(
        f"https://{web_url}.mobidziennik.pl/mobile/oceny?semestr=2", data=data
    )
    tree = html.fromstring(web.content)
    root = tree.xpath('//tr[@class="subject"]/td')
    for i in root:
        try:
            i = float(i.text.strip())
        except ValueError:
            if i.text.strip() != "":
                mobi.marks_avg_name2.append(i.text)
                mobi.marks_avg2.append(i.getparent().getchildren()[2].text.strip())

    web = requests.post(
        f"https://{web_url}.mobidziennik.pl/mobile/oceny?semestr=2&koncowe", data=data
    )
    tree = html.fromstring(web.content)
    root = tree.xpath('//span[@class="color-red"]/../..')
    for i in root:
        i = i.getchildren()
        if i[0].text.strip() != "Śródroczna":
            mobi.red_names2.append(i[0].getchildren()[0].tail.strip())
            mobi.red_marks2.append(i[1].getchildren()[0].text.strip())

    avg_counter = 0
    for i in range(len(mobi.marks_avg2)):
        if mobi.marks_avg2[i] != "":
            try:
                index = mobi.red_names2.index(mobi.marks_avg_name2[i])
                przedmiot = mobi.red_marks2[index]
                przedmiot = await correct_mark(przedmiot)
            except ValueError:
                przedmiot = mobi.marks_avg2[i]
            try:
                przedmiot = float(przedmiot)
                mobi.avg2 += float(przedmiot)
                avg_counter += 1
            except ValueError:
                pass
    if avg_counter > 0:
        mobi.avg2 = str(mobi.avg2 / avg_counter)[:4]
    else:
        mobi.avg2 = ""


async def get_timetables(mobi, data, web_url):
    web = requests.post(
        f"https://{web_url}.mobidziennik.pl/mobile/planlekcji?typ=podstawowy", data=data
    )
    tree = html.fromstring(web.content)
    root = tree.xpath('//td[@class="padding-l-15"]/span/strong')
    found = 0
    for i in root:
        lessons_date = (
            i.getparent()
            .getparent()
            .getparent()
            .getparent()
            .getparent()
            .getparent()
            .getparent()
            .getparent()
            .getparent()
            .getchildren()[0]
            .getchildren()[0]
            .getchildren()[0]
            .tail
        )
        lessons_date = lessons_date.strip()[3:]
        today = date.today().day
        day_name = (
            i.getparent()
            .getparent()
            .getparent()
            .getparent()
            .getparent()
            .getparent()
            .getparent()
            .getparent()
            .getparent()
            .getchildren()[0]
            .getchildren()[0]
            .getchildren()[0]
            .text.lower()
        )
        lessons_date = await get_day(lessons_date)
        time = datetime.now().time().hour
        if time > 15:
            if (
                lessons_date == today + 1
                and found == 0
                or lessons_date == today + 1
                and found == lessons_date
            ):
                hour = (
                    i.getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getchildren()[0]
                    .getchildren()[0]
                    .tail.strip()
                )
                room = i.getparent().getchildren()[1].tail
                teacher = await get_teacher(room)
                room = await get_classroom(room)
                if (
                    i.getparent().get("style")
                    == "text-decoration: line-through;opacity:0.8;"
                ):
                    tbody = (
                        i.getparent().getparent().getparent().getparent().getchildren()
                    )
                    if len(tbody) > 1:
                        change_name = tbody[1].getchildren()[0].getchildren()[3].text
                        room = tbody[1].getchildren()[0].getchildren()[5].text
                        teacher = await get_teacher(room)
                        room = await get_classroom(room)
                        mobi.teachers.append(teacher)
                        mobi.lessons[0].append(
                            f"[color=#ffff00]{change_name}{room}[/color]"
                        )
                        mobi.lessons[1].append(f"[color=#ffff00]{hour}[/color]")
                    else:
                        mobi.teachers.append(teacher)
                        mobi.lessons[0].append(
                            f"[s][color=#ff0000]{i.text}{room}[/color][/s]"
                        )
                        mobi.lessons[1].append(f"[s][color=#ff0000]{hour}[/color][/s]")
                else:
                    mobi.teachers.append(teacher)
                    mobi.lessons[0].append(f"{i.text}{room}")
                    mobi.lessons[1].append(hour)
                mobi.lessons[2] = f"Plan lekcji na {day_name}"
                found = lessons_date
            elif (
                lessons_date == today + 2
                and found == 0
                or lessons_date == today + 2
                and found == lessons_date
            ):
                hour = (
                    i.getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getchildren()[0]
                    .getchildren()[0]
                    .tail.strip()
                )
                room = i.getparent().getchildren()[1].tail
                teacher = await get_teacher(room)
                room = await get_classroom(room)
                if (
                    i.getparent().get("style")
                    == "text-decoration: line-through;opacity:0.8;"
                ):
                    tbody = (
                        i.getparent().getparent().getparent().getparent().getchildren()
                    )
                    if len(tbody) > 1:
                        change_name = tbody[1].getchildren()[0].getchildren()[3].text
                        room = tbody[1].getchildren()[0].getchildren()[5].text
                        teacher = await get_teacher(room)
                        room = await get_classroom(room)
                        mobi.teachers.append(teacher)
                        mobi.lessons[0].append(
                            f"[color=#ffff00]{change_name}{room}[/color]"
                        )
                        mobi.lessons[1].append(f"[color=#ffff00]{hour}[/color]")
                    else:
                        mobi.teachers.append(teacher)
                        mobi.lessons[0].append(
                            f"[s][color=#ff0000]{i.text}{room}[/color][/s]"
                        )
                        mobi.lessons[1].append(f"[s][color=#ff0000]{hour}[/color][/s]")
                else:
                    mobi.teachers.append(teacher)
                    mobi.lessons[0].append(f"{i.text}{room}")
                    mobi.lessons[1].append(hour)
                mobi.lessons[2] = f"Plan lekcji na {day_name}"
                found = lessons_date
            elif (
                lessons_date == today + 3
                and found == 0
                or lessons_date == today + 3
                and found == lessons_date
            ):
                hour = (
                    i.getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getchildren()[0]
                    .getchildren()[0]
                    .tail.strip()
                )
                room = i.getparent().getchildren()[1].tail
                teacher = await get_teacher(room)
                room = await get_classroom(room)
                if (
                    i.getparent().get("style")
                    == "text-decoration: line-through;opacity:0.8;"
                ):
                    tbody = (
                        i.getparent().getparent().getparent().getparent().getchildren()
                    )
                    if len(tbody) > 1:
                        change_name = tbody[1].getchildren()[0].getchildren()[3].text
                        room = tbody[1].getchildren()[0].getchildren()[5].text
                        teacher = await get_teacher(room)
                        room = await get_classroom(room)
                        mobi.teachers.append(teacher)
                        mobi.lessons[0].append(
                            f"[color=#ffff00]{change_name}{room}[/color]"
                        )
                        mobi.lessons[1].append(f"[color=#ffff00]{hour}[/color]")
                    else:
                        mobi.teachers.append(teacher)
                        mobi.lessons[0].append(
                            f"[s][color=#ff0000]{i.text}{room}[/color][/s]"
                        )
                        mobi.lessons[1].append(f"[s][color=#ff0000]{hour}[/color][/s]")
                else:
                    mobi.teachers.append(teacher)
                    mobi.lessons[0].append(f"{i.text}{room}")
                    mobi.lessons[1].append(hour)
                mobi.lessons[2] = f"Plan lekcji na {day_name}"
                found = lessons_date
            elif (
                lessons_date == today + 4
                and found == 0
                or lessons_date == today + 4
                and found == lessons_date
            ):
                hour = (
                    i.getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getchildren()[0]
                    .getchildren()[0]
                    .tail.strip()
                )
                room = i.getparent().getchildren()[1].tail
                teacher = await get_teacher(room)
                room = await get_classroom(room)
                if (
                    i.getparent().get("style")
                    == "text-decoration: line-through;opacity:0.8;"
                ):
                    tbody = (
                        i.getparent().getparent().getparent().getparent().getchildren()
                    )
                    if len(tbody) > 1:
                        change_name = tbody[1].getchildren()[0].getchildren()[3].text
                        room = tbody[1].getchildren()[0].getchildren()[5].text
                        teacher = await get_teacher(room)
                        room = await get_classroom(room)
                        mobi.teachers.append(teacher)
                        mobi.lessons[0].append(
                            f"[color=#ffff00]{change_name}{room}[/color]"
                        )
                        mobi.lessons[1].append(f"[color=#ffff00]{hour}[/color]")
                    else:
                        mobi.teachers.append(teacher)
                        mobi.lessons[0].append(
                            f"[s][color=#ff0000]{i.text}{room}[/color][/s]"
                        )
                        mobi.lessons[1].append(f"[s][color=#ff0000]{hour}[/color][/s]")
                else:
                    mobi.teachers.append(teacher)
                    mobi.lessons[0].append(f"{i.text}{room}")
                    mobi.lessons[1].append(hour)
                mobi.lessons[2] = f"Plan lekcji na {day_name}"
                found = lessons_date
        else:
            if (
                lessons_date == today
                and found == 0
                or lessons_date == today
                and found == lessons_date
            ):
                hour = (
                    i.getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getchildren()[0]
                    .getchildren()[0]
                    .tail.strip()
                )
                room = i.getparent().getchildren()[1].tail
                teacher = await get_teacher(room)
                room = await get_classroom(room)
                if (
                    i.getparent().get("style")
                    == "text-decoration: line-through;opacity:0.8;"
                ):
                    tbody = (
                        i.getparent().getparent().getparent().getparent().getchildren()
                    )
                    if len(tbody) > 1:
                        change_name = tbody[1].getchildren()[0].getchildren()[3].text
                        room = tbody[1].getchildren()[0].getchildren()[5].text
                        teacher = await get_teacher(room)
                        room = await get_classroom(room)
                        mobi.teachers.append(teacher)
                        mobi.lessons[0].append(
                            f"[color=#ffff00]{change_name}{room}[/color]"
                        )
                        mobi.lessons[1].append(f"[color=#ffff00]{hour}[/color]")
                    else:
                        mobi.teachers.append(teacher)
                        mobi.lessons[0].append(
                            f"[s][color=#ff0000]{i.text}{room}[/color][/s]"
                        )
                        mobi.lessons[1].append(f"[s][color=#ff0000]{hour}[/color][/s]")
                else:
                    mobi.teachers.append(teacher)
                    mobi.lessons[0].append(f"{i.text}{room}")
                    mobi.lessons[1].append(hour)
                mobi.lessons[2] = "Plan lekcji na dziś:"
                found = lessons_date
            elif (
                lessons_date == today + 1
                and found == 0
                or lessons_date == today + 1
                and found == lessons_date
            ):
                hour = (
                    i.getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getchildren()[0]
                    .getchildren()[0]
                    .tail.strip()
                )
                room = i.getparent().getchildren()[1].tail
                teacher = await get_teacher(room)
                room = await get_classroom(room)
                if (
                    i.getparent().get("style")
                    == "text-decoration: line-through;opacity:0.8;"
                ):
                    tbody = (
                        i.getparent().getparent().getparent().getparent().getchildren()
                    )
                    if len(tbody) > 1:
                        change_name = tbody[1].getchildren()[0].getchildren()[3].text
                        room = tbody[1].getchildren()[0].getchildren()[5].text
                        teacher = await get_teacher(room)
                        room = await get_classroom(room)
                        mobi.teachers.append(teacher)
                        mobi.lessons[0].append(
                            f"[color=#ffff00]{change_name}{room}[/color]"
                        )
                        mobi.lessons[1].append(f"[color=#ffff00]{hour}[/color]")
                    else:
                        mobi.teachers.append(teacher)
                        mobi.lessons[0].append(
                            f"[s][color=#ff0000]{i.text}{room}[/color][/s]"
                        )
                        mobi.lessons[1].append(f"[s][color=#ff0000]{hour}[/color][/s]")
                else:
                    mobi.teachers.append(teacher)
                    mobi.lessons[0].append(f"{i.text}{room}")
                    mobi.lessons[1].append(hour)
                mobi.lessons[2] = f"Plan lekcji na {day_name}"
                found = lessons_date
            elif (
                lessons_date == today + 2
                and found == 0
                or lessons_date == today + 2
                and found == lessons_date
            ):
                hour = (
                    i.getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getparent()
                    .getchildren()[0]
                    .getchildren()[0]
                    .tail.strip()
                )
                room = i.getparent().getchildren()[1].tail
                teacher = await get_teacher(room)
                room = await get_classroom(room)
                if (
                    i.getparent().get("style")
                    == "text-decoration: line-through;opacity:0.8;"
                ):
                    tbody = (
                        i.getparent().getparent().getparent().getparent().getchildren()
                    )
                    if len(tbody) > 1:
                        change_name = tbody[1].getchildren()[0].getchildren()[3].text
                        room = tbody[1].getchildren()[0].getchildren()[5].text
                        teacher = await get_teacher(room)
                        room = await get_classroom(room)
                        mobi.teachers.append(teacher)
                        mobi.lessons[0].append(
                            f"[color=#ffff00]{change_name}{room}[/color]"
                        )
                        mobi.lessons[1].append(f"[color=#ffff00]{hour}[/color]")
                    else:
                        mobi.teachers.append(teacher)
                        mobi.lessons[0].append(
                            f"[s][color=#ff0000]{i.text}{room}[/color][/s]"
                        )
                        mobi.lessons[1].append(f"[s][color=#ff0000]{hour}[/color][/s]")
                else:
                    mobi.teachers.append(teacher)
                    mobi.lessons[0].append(f"{i.text}{room}")
                    mobi.lessons[1].append(hour)
                mobi.lessons[2] = f"Plan lekcji na {day_name}"
                found = lessons_date


async def get_exams(mobi, data, web_url):
    web = requests.post(
        f"https://{web_url}.mobidziennik.pl/mobile/sprawdziany", data=data
    )
    tree = html.fromstring(web.content)
    root = tree.xpath('//div[@class="brd"]')
    for x in root:
        x = x.getparent().getparent().getchildren()
        date_exam = x[0].getchildren()[0].tail.strip()
        sub_exam = x[1].text.strip()
        topic_exam = x[2].text.strip()
        mobi.exams.append([date_exam, sub_exam, topic_exam])


async def get_homeworks(mobi, data, web_url):
    web = requests.post(
        f"https://{web_url}.mobidziennik.pl/mobile/zadaniadomowe", data=data
    )
    tree = html.fromstring(web.content)
    root = tree.xpath('//div[@class="brd"]')
    for x in root:
        x = x.getparent().getparent().getchildren()
        date_hw = x[0].getchildren()[0].tail.strip()
        sub_hw = x[1].text.strip()
        topic_hw = x[2].text.strip()
        mobi.homeworks.append([date_hw, sub_hw, topic_hw])


async def get_messages(mobi, data, web_url):
    web = requests.post(
        f"https://{web_url}.mobidziennik.pl/mobile/wiadomosci?js", data=data
    )
    tree = html.fromstring(web.content)
    root = tree.xpath('//div[@class="brd"]')[:5]
    for message in root:
        mobi.message_titles.append(message.tail.strip())
        mobi.message_sender.append(
            message.getparent().getparent().getchildren()[2].text.strip()
        )
        id = message.getparent().getparent().get("data-page")
        message_web = requests.post(
            f"https://{web_url}.mobidziennik.pl/mobile/{id}", data=data
        )
        message_root = html.fromstring(message_web.content)
        message_root = message_root.xpath('//div[@class="acc-elm-body"]')[
            0
        ].getchildren()[:-1]
        if len(message_root) > 1:
            full_message = ""
            for mess in message_root:
                try:
                    full_message += (
                        mess.getchildren()[0].getchildren()[0].getchildren()[0].text
                    )
                    full_message += "\n"
                except IndexError:
                    try:
                        full_message += mess.getchildren()[0].getchildren()[0].text
                    except IndexError:
                        try:
                            full_message += mess.getchildren()[0].text
                        except IndexError:
                            full_message += mess.text
                    full_message += "\n"
            mobi.messages.append(full_message)
        else:
            mobi.messages.append(message_root[0].text)
