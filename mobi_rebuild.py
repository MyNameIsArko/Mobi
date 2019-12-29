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
from cryptography.fernet import Fernet


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
            new_mark = f'{int(mark[0])-1}.75'
            return new_mark
        if mark[1] == '+':
            new_mark = f'{int(mark[0])}.50'
            return new_mark
    else:
        return mark


isFile = False
last_marks, last_marks_name, description, marks_avg, marks_avg_name, avg = [], [], [], [], [], ''
red_names, red_marks = [], []


def website(data, web_url):
    global last_marks
    global last_marks_name
    global description
    global marks_avg
    global marks_avg_name
    global avg
    global red_marks
    global red_names
    web = requests.post(f'https://{web_url}.mobidziennik.pl/mobile/glowna', data=data)
    tree = html.fromstring(web.content)
    last_marks = tree.xpath('//td[@class="page-dz-home-hist-cnt text-center"]/../..')[0]
    last_marks = last_marks.getchildren()
    last_marks = [mark.getchildren() for mark in last_marks][:6]
    for i in range(6):
        if i % 2 == 0:
            last_marks_name.append(last_marks[i][1].text)
            last_marks[i] = last_marks[i][2].text
        else:
            description.append(last_marks[i][0].getchildren()[0].getchildren()[0].getchildren()[2].getchildren()[0].tail)
    last_marks = [mark for mark in last_marks if isinstance(mark, str)]
    last_marks = SpaceRemover(last_marks)
    last_marks_name = SpaceRemover(last_marks_name)
    web = requests.post(f'https://{web_url}.mobidziennik.pl/mobile/oceny', data=data)
    tree = html.fromstring(web.content)
    marks_avg = tree.xpath('//td[@class="text-right"]/text()')
    marks_avg = SpaceRemover(marks_avg)
    marks_avg_name = tree.xpath('//tr[@class="subject"]/td/text()')
    marks_avg_name = SpaceRemover(marks_avg_name)

    web = requests.post(f'https://{web_url}.mobidziennik.pl/mobile/oceny?semestr=1&koncowe', data=data)
    tree = html.fromstring(web.content)
    path = tree.xpath('//td[@class="text-right"]')
    for x in path:
        y = x.getchildren()
        try:
            if y[0].get('class') == 'color-red':
                parent = y[0].getparent().getparent()
                red_names.append(parent.getchildren()[0].getchildren()[0].tail)
                red_marks.append(parent.getchildren()[1].getchildren()[0].text)
        except IndexError:
            pass
    red_marks = SpaceRemover(red_marks)
    red_names = SpaceRemover(red_names)

    for i in range(len(marks_avg_name)):
        if marks_avg_name[i] == 'godzina z wychowawcą':
            marks_avg.insert(i, "")
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
        box_main = BoxLayout(orientation='vertical')

        last_label = Label(text='Ostatnie oceny:', bold=True)
        box_main.add_widget(last_label)
        for i in range(3):
            last_box = BoxLayout(orientation='horizontal', on_touch_down=self.test)
            name_label = Label(text=last_marks_name[i], text_size=(600, 200), valign='center', halign='right')
            mark_label = Label(text=last_marks[i])
            last_box.add_widget(name_label)
            last_box.add_widget(mark_label)
            box_main.add_widget(last_box)

        marks_avg_label = Label(text='Srednie ocen z przedmiotow:', bold=True)
        box_main.add_widget(marks_avg_label)

        for i in range(len(marks_avg_name)):
            mark_avg_box = BoxLayout(orientation='horizontal')
            name_label = Label(text=marks_avg_name[i], text_size=(600, 200), valign='center', halign='right')
            try:
                index = red_names.index(marks_avg_name[i])
                mark_avg_label = Label(text=red_marks[index], color=[1, 0, 0, 1])
            except ValueError:
                mark_avg_label = Label(text=marks_avg[i])
            mark_avg_box.add_widget(name_label)
            mark_avg_box.add_widget(mark_avg_label)
            box_main.add_widget(mark_avg_box)
        avg_box = BoxLayout(orientation='horizontal')
        avg_name_label = Label(text='Srednia polroczna:', text_size=(600, 200), valign='center', halign='right',
                               bold=True)
        avg_label = Label(text=avg)
        avg_box.add_widget(avg_name_label)
        avg_box.add_widget(avg_label)
        box_main.add_widget(avg_box)

        self.add_widget(box_main)


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
        data = {'login': self.login_input.text, 'haslo': self.password_input.text}
        web_url = self.web_url.text
        web = requests.post(f'https://{web_url}.mobidziennik.pl/mobile/glowna', data=data)
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
