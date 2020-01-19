import requests
from lxml import html
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.carousel import Carousel
from cryptography.fernet import Fernet
from datetime import date, datetime


def SpaceRemover(tab):
    i = 0
    while i < len(tab):
        if tab[i].strip() == "":
            del tab[i]
        else:
            tab[i] = tab[i].strip()
            i += 1
    return tab


def correct_mark(mark):
    if len(mark) > 1:
        if mark[1] == '-':
            new_mark = f'{int(mark[0]) - 1}.75'
            return new_mark
        if mark[1] == '+':
            new_mark = f'{int(mark[0])}.50'
            return new_mark
    else:
        return mark


def get_day(string):
    day = ''
    for i in string:
        try:
            int(i)
            day += i
        except ValueError:
            break
    return int(day)


def get_month(index):
    months = ['', 'stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca', 'lipca', 'sierpnia', 'września',
              'października', 'listopada', 'grudnia']
    return months[index]


def get_classroom(tail):
    tail = tail.strip()
    i = len(tail) - 1
    room = []
    while i > 0:
        if tail[i] == '(':
            room.insert(0, tail[i])
            break
        else:
            room.insert(0, tail[i])
        i -= 1
    return ''.join(room)


isFile = False
last_marks, last_marks_name, description, marks_avg, marks_avg_name, avg = [], [], [], [], [], ''
red_names, red_marks = [], []
lessons = [[], [], []]
homeworks, exams = [], []


def website(data, web_url):
    global last_marks
    global last_marks_name
    global description
    global marks_avg
    global marks_avg_name
    global avg
    global red_marks
    global red_names
    global lessons
    global homeworks
    global exams
    try:
        web = requests.post(f'https://{web_url}.mobidziennik.pl/mobile/glowna', data=data)
        tree = html.fromstring(web.content)
        root = tree.xpath('//td[@class="page-dz-home-hist-cnt"]/../..')
        for i in root:
            for y in i:
                if y.get('class') == 'rowRolling':
                    y = y.getchildren()[0].getchildren()[0].getchildren()[0].getchildren()
                    for z in y:
                        z = z.getchildren()[0]
                        if z.text == 'Grupa:' or z.text == 'Rodzaj:' or z.text == 'Treść:':
                            description.append(z.tail)
                else:
                    y = y.getchildren()[1:]
                    for z in y:
                        if z.get('class') == 'page-dz-home-hist-cnt':
                            last_marks_name.append(z.text)
                        else:
                            last_marks.append(z.text)
        last_marks = last_marks[:3]
        last_marks_name = last_marks_name[:3]
        description = description[:3]
        last_marks = SpaceRemover(last_marks)
        last_marks_name = SpaceRemover(last_marks_name)
    except:
        pass
    web = requests.post(f'https://{web_url}.mobidziennik.pl/mobile/oceny', data=data)
    tree = html.fromstring(web.content)
    root = tree.xpath('//tr[@class="subject"]/td/text()')
    for i in root:
        if 'wychowaw' in i:
            marks_avg.append('')
        try:
            marks_avg.append(float(i))
        except:
            marks_avg_name.append(i)
    marks_avg_name = SpaceRemover(marks_avg_name)
    web = requests.post(f'https://{web_url}.mobidziennik.pl/mobile/oceny?semestr=1&koncowe', data=data)
    tree = html.fromstring(web.content)
    root = tree.xpath('//span[@class="color-red"]/../..')
    for i in root:
        i = i.getchildren()
        if i[0].text.strip() != 'Śródroczna':
            red_names.append(i[0].getchildren()[0].tail.strip())
            red_marks.append(i[1].getchildren()[0].text.strip())
    avg = 0
    avgCounter = 0
    for i in range(len(marks_avg)):
        if marks_avg[i] != "":
            try:
                index = red_names.index(marks_avg_name[i])
                przedmiot = red_marks[index]
                przedmiot = correct_mark(przedmiot)
            except ValueError:
                przedmiot = marks_avg[i]
            avg += float(przedmiot)
            avgCounter += 1
    avg = str(avg / avgCounter)[:4]

    web = requests.post(f'https://{web_url}.mobidziennik.pl/mobile/planlekcji?typ=podstawowy', data=data)
    tree = html.fromstring(web.content)
    root = tree.xpath('//td[@class="padding-l-15"]/span/strong')
    found = 0
    for i in root:
        lessons_date = \
            i.getparent().getparent().getparent().getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[
                0].getchildren()[0].getchildren()[0].tail
        lessons_date = lessons_date.strip()[3:]
        today = date.today().day
        day_name = \
            i.getparent().getparent().getparent().getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[
                0].getchildren()[0].getchildren()[0].text.lower()
        lessons_date = get_day(lessons_date)
        time = datetime.now().time().hour
        if time > 16:
            if lessons_date == today + 1 and found == 0 or lessons_date == today + 1 and found == lessons_date:
                hour = i.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[
                    0].getchildren()[0].tail.strip()
                room = i.getparent().getchildren()[1].tail
                room = get_classroom(room)
                if i.getparent().get('style') == 'text-decoration: line-through;opacity:0.8;':
                    lessons[0].append(f'[s][color=#ff0000]{i.text}{room}[/color][/s]')
                    lessons[1].append(f'[s][color=#ff0000]{hour}[/color][/s]')
                else:
                    lessons[0].append(f'{i.text}{room}')
                    lessons[1].append(hour)
                lessons[2] = f'Plan lekcji na {day_name}'
                found = lessons_date
            elif lessons_date == today + 2 and found == 0 or lessons_date == today + 2 and found == lessons_date:
                hour = i.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[
                    0].getchildren()[0].tail.strip()
                room = i.getparent().getchildren()[1].tail
                room = get_classroom(room)
                if i.getparent().get('style') == 'text-decoration: line-through;opacity:0.8;':
                    lessons[0].append(f'[s][color=#ff0000]{i.text}{room}[/color][/s]')
                    lessons[1].append(f'[s][color=#ff0000]{hour}[/color][/s]')
                else:
                    lessons[0].append(f'{i.text}{room}')
                    lessons[1].append(hour)
                lessons[2] = f'Plan lekcji na {day_name}'
                found = lessons_date
            elif lessons_date == today + 3 and found == 0 or lessons_date == today + 3 and found == lessons_date:
                hour = i.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[
                    0].getchildren()[0].tail.strip()
                room = i.getparent().getchildren()[1].tail
                room = get_classroom(room)
                if i.getparent().get('style') == 'text-decoration: line-through;opacity:0.8;':
                    lessons[0].append(f'[s][color=#ff0000]{i.text}{room}[/color][/s]')
                    lessons[1].append(f'[s][color=#ff0000]{hour}[/color][/s]')
                else:
                    lessons[0].append(f'{i.text}{room}')
                    lessons[1].append(hour)
                lessons[2] = f'Plan lekcji na {day_name}'
                found = lessons_date
        else:
            if lessons_date == today and found == 0 or lessons_date == today and found == lessons_date:
                hour = i.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[
                    0].getchildren()[0].tail.strip()
                room = i.getparent().getchildren()[1].tail
                room = get_classroom(room)
                if i.getparent().get('style') == 'text-decoration: line-through;opacity:0.8;':
                    lessons[0].append(f'[s][color=#ff0000]{i.text}{room}[/color][/s]')
                    lessons[1].append(f'[s][color=#ff0000]{hour}[/color][/s]')
                else:
                    lessons[0].append(f'{i.text}{room}')
                    lessons[1].append(hour)
                lessons[2] = 'Plan lekcji na dziś:'
                found = lessons_date
            elif lessons_date == today + 1 and found == 0 or lessons_date == today + 1 and found == lessons_date:
                hour = i.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[
                    0].getchildren()[0].tail.strip()
                room = i.getparent().getchildren()[1].tail
                room = get_classroom(room)
                if i.getparent().get('style') == 'text-decoration: line-through;opacity:0.8;':
                    lessons[0].append(f'[s][color=#ff0000]{i.text}{room}[/color][/s]')
                    lessons[1].append(f'[s][color=#ff0000]{hour}[/color][/s]')
                else:
                    lessons[0].append(f'{i.text}{room}')
                    lessons[1].append(hour)
                lessons[2] = f'Plan lekcji na {day_name}'
                found = lessons_date
            elif lessons_date == today + 2 and found == 0 or lessons_date == today + 2 and found == lessons_date:
                hour = i.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[
                    0].getchildren()[0].tail.strip()
                room = i.getparent().getchildren()[1].tail
                room = get_classroom(room)
                if i.getparent().get('style') == 'text-decoration: line-through;opacity:0.8;':
                    lessons[0].append(f'[s][color=#ff0000]{i.text}{room}[/color][/s]')
                    lessons[1].append(f'[s][color=#ff0000]{hour}[/color][/s]')
                else:
                    lessons[0].append(f'{i.text}{room}')
                    lessons[1].append(hour)
                lessons[2] = f'Plan lekcji na {day_name}'
                found = lessons_date

    web = requests.post(f'https://{web_url}.mobidziennik.pl/mobile/sprawdziany', data=data)
    tree = html.fromstring(web.content)
    root = tree.xpath('//div[@class="brd"]')
    for x in root:
        x = x.getparent().getparent().getchildren()
        date_exam = x[0].getchildren()[0].tail.strip()
        sub_exam = x[1].text.strip()
        topic_exam = x[2].text.strip()
        exams.append([date_exam, sub_exam, topic_exam])

    web = requests.post(f'https://{web_url}.mobidziennik.pl/mobile/zadaniadomowe', data=data)
    tree = html.fromstring(web.content)
    root = tree.xpath('//div[@class="brd"]')
    for x in root:
        x = x.getparent().getparent().getchildren()
        date_hw = x[0].getchildren()[0].tail.strip()
        sub_hw = x[1].text.strip()
        topic_hw = x[2].text.strip()
        homeworks.append([date_hw, sub_hw, topic_hw])


class ErrorPopup(Popup):
    def __init__(self, mess, *args, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Błąd!'
        self.title_align = 'center'
        self.size_hint = [None, None]
        self.width = 800
        self.height = 400
        self.add_widget(Label(text=mess))


try:
    with open('mobi.b', 'rb') as file:
        isFile = True
        key = file.readline()[:-1]
        f = Fernet(key)
        login = file.readline()[:-1]
        login = f.decrypt(login)
        login = login.decode()
        password = file.readline()[:-1]
        password = f.decrypt(password)
        password = password.decode()
        data = {'login': login, 'haslo': password}
        web_url = file.readline()
        web_url = f.decrypt(web_url)
        web_url = web_url.decode()
        website(data, web_url)
except FileNotFoundError:
    isFile = False
except Exception as e:
    ErrorPopup(str(e)).open()


class LastPopup(Popup):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.title = args[0].children[1].text
        self.title_align = 'center'
        self.size_hint = [None, None]
        self.width = 800
        self.height = 400
        index = last_marks_name.index(args[0].children[1].text)
        desc = description[index]
        self.add_widget(Label(text=desc))


class MainWindow(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = 'main'

    def test(self, *args):
        if args[0].collide_point(args[1].x, args[1].y):
            LastPopup(args[0]).open()

    def on_pre_enter(self, *args):
        try:
            carousel = Carousel(direction='right', loop=True)
            box_main = BoxLayout(orientation='vertical')

            last_label = Label(text='Ostatnie oceny:', bold=True)
            box_main.add_widget(last_label)
            for i in range(len(last_marks)):
                last_box = BoxLayout(orientation='horizontal', on_touch_down=self.test)
                name_label = Label(text=str(last_marks_name[i]), text_size=(600, 200), valign='center', halign='right')
                mark_label = Label(text=str(last_marks[i]))
                last_box.add_widget(name_label)
                last_box.add_widget(mark_label)
                box_main.add_widget(last_box)

            marks_avg_label = Label(text='Srednie ocen z przedmiotow:', bold=True)
            box_main.add_widget(marks_avg_label)

            for i in range(len(marks_avg_name)):
                mark_avg_box = BoxLayout(orientation='horizontal')
                name_label = Label(text=str(marks_avg_name[i]), text_size=(600, 200), valign='center', halign='right')
                try:
                    index = red_names.index(marks_avg_name[i])
                    mark_avg_label = Label(text=str(red_marks[index]), color=[1, 0, 0, 1])
                except ValueError:
                    mark_avg_label = Label(text=str(marks_avg[i]))
                mark_avg_box.add_widget(name_label)
                mark_avg_box.add_widget(mark_avg_label)
                box_main.add_widget(mark_avg_box)
            avg_box = BoxLayout(orientation='horizontal')
            avg_name_label = Label(text='Srednia polroczna:', text_size=(600, 200), valign='center', halign='right',
                                   bold=True)
            avg_label = Label(text=str(avg))
            avg_box.add_widget(avg_name_label)
            avg_box.add_widget(avg_label)
            box_main.add_widget(avg_box)
            carousel.add_widget(box_main)
            timetable = BoxLayout(orientation='vertical')
            timetable.add_widget(Label(text=f'[b]{lessons[2]}[/b]', markup=True, font_size=55))
            for i, j in zip(lessons[0], lessons[1]):
                lh = BoxLayout(orientation='horizontal')
                lh.add_widget(Label(text=str(i), markup=True, text_size=(500, 200), valign='center', halign='right'))
                lh.add_widget(Label(text=str(j), markup=True))
                timetable.add_widget(lh)
            carousel.add_widget(timetable)
            exam_box = BoxLayout(orientation='vertical')
            exam_box.add_widget(Label(text='[b]Sprawdziany: [/b]', markup=True, font_size=55))
            for i in exams:
                exam_cont = BoxLayout(orientation='horizontal')
                exam_cont.add_widget(Label(text=str(i[0])))
                exam_cont.add_widget(Label(text=str(i[1])))
                exam_cont.add_widget(Label(text=str(i[2])))
                exam_box.add_widget(exam_cont)
            homework_box = BoxLayout(orientation='vertical')
            homework_box.add_widget(Label(text='[b]Zadania domowe: [/b]', markup=True, font_size=55))
            for i in homeworks:
                homework_cont = BoxLayout(orientation='horizontal')
                homework_cont.add_widget(Label(text=str(i[0])))
                homework_cont.add_widget(Label(text=str(i[1])))
                homework_cont.add_widget(Label(text=str(i[2])))
                homework_box.add_widget(homework_cont)
            container = BoxLayout(orientation='vertical')
            container.add_widget(exam_box)
            container.add_widget(homework_box)
            container.add_widget(Widget())
            carousel.add_widget(container)
            self.add_widget(carousel)
        except Exception as e:
            ErrorPopup(str(e)).open()


class SignInWindow(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = "sign in"
        box_main = BoxLayout(orientation='vertical', padding=50, spacing=100)
        box_main.add_widget(Widget(size_hint_y=None, height=200))
        web_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=70, pos_hint={'top': 1})
        web_label = Label(text='Adres:')
        self.web_url = TextInput(multiline=False, size_hint_x=None, width=400)
        web_end = Label(text='.mobidziennik.pl', size_hint_x=None, width=400)
        web_box.add_widget(web_label)
        web_box.add_widget(self.web_url)
        web_box.add_widget(web_end)
        login_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=70, pos_hint={'top': 1})
        login_label = Label(text='Login:')
        self.login_input = TextInput(multiline=False)
        login_box.add_widget(login_label)
        login_box.add_widget(self.login_input)

        password_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=70)
        password_label = Label(text='Haslo:')
        self.password_input = TextInput(multiline=False, password=True)
        password_box.add_widget(password_label)
        password_box.add_widget(self.password_input)
        box_main.add_widget(web_box)
        box_main.add_widget(login_box)
        box_main.add_widget(password_box)

        sign_button = Button(text='Zaloguj', on_press=self.sign, size_hint_y=None, height=140)
        box_main.add_widget(sign_button)
        box_main.add_widget(Widget())
        self.add_widget(box_main)

    def sign(self, *args):
        try:
            data = {'login': self.login_input.text, 'haslo': self.password_input.text}
            web_url = self.web_url.text
            web = requests.post(f'https://{web_url}.mobidziennik.pl/mobile/glowna', data=data)
            if web.url == f'https://mobidziennik.pl/zlyadres.php?adres={web_url}.mobidziennik.pl':
                ErrorPopup('Podano zły adres!').open()
            else:
                tree = html.fromstring(web.content)
                test = tree.xpath('//div[@id="p-login-info-text"]/text()')
                if not test:
                    website(data, web_url)
                    key = Fernet.generate_key()
                    with open('mobi.b', 'wb') as file:
                        file.write(key)
                        file.write(b'\n')
                        f = Fernet(key)
                        login = data.get('login')
                        login = login.encode()
                        login = f.encrypt(login)
                        password = data.get('haslo')
                        password = password.encode()
                        password = f.encrypt(password)
                        web_url = web_url.encode()
                        web_url = f.encrypt(web_url)
                        file.write(login)
                        file.write(b'\n')
                        file.write(password)
                        file.write(b'\n')
                        file.write(web_url)
                    self.parent.current = "main"
                else:
                    ErrorPopup('Podano błędne dane logowania').open()
                    self.screen = "sign in"
        except UnicodeError:
            ErrorPopup('Adres nie może być pusty').open()
            self.screen = "sign in"


class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(SignInWindow())
        self.add_widget(MainWindow())
        if isFile:
            self.current = 'main'


class Mobi(App):
    def build(self):
        return WindowManager(transition=FadeTransition())


mobi = Mobi()
