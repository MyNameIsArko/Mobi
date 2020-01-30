import asyncio

from cryptography.fernet import Fernet

from functions import *
import requests
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.carousel import Carousel
from lxml import html

from mobi import Mobi

mobi = Mobi()


class ErrorPopup(Popup):
    def __init__(self, mess, *args, **kwargs):
        super().__init__(**kwargs)
        self.title = "Błąd!"
        self.title_align = "center"
        self.size_hint = [None, None]
        self.width = 800
        self.height = 400
        self.add_widget(Label(text=mess))


try:
    with open("mobi.b", "rb") as file:
        mobi.isFile = True
        key = file.readline()[:-1]
        f = Fernet(key)
        login = file.readline()[:-1]
        login = f.decrypt(login)
        login = login.decode()
        password = file.readline()[:-1]
        password = f.decrypt(password)
        password = password.decode()
        data = {"login": login, "haslo": password}
        web_url = file.readline()
        web_url = f.decrypt(web_url)
        web_url = web_url.decode()
        asyncio.get_event_loop().run_until_complete(
            asyncio.gather(
                get_last_marks(mobi, data, web_url),
                get_first_marks(mobi, data, web_url),
                get_second_marks(mobi, data, web_url),
                get_timetables(mobi, data, web_url),
                get_exams(mobi, data, web_url),
                get_homeworks(mobi, data, web_url),
                get_messages(mobi, data, web_url),
            )
        )
except FileNotFoundError:
    mobi.isFile = False
except Exception as e:
    ErrorPopup(str(e)).open()


class LastPopup(Popup):
    def __init__(self, text, *args, **kwargs):
        super().__init__(**kwargs)
        self.title = text
        self.title_align = "center"
        self.size_hint = [None, None]
        self.width = 800
        self.height = 400
        index = mobi.last_marks_name.index(text)
        desc = mobi.description[index]
        self.add_widget(Label(text=desc))


class TeacherPopup(Popup):
    def __init__(self, title, text, *args, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.markup = True
        self.title_align = "center"
        self.size_hint = [None, None]
        self.width = 800
        self.height = 400
        self.add_widget(Label(text=text))


class MessagePopup(Popup):
    def __init__(self, title, text, *args, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.title_align = "center"
        self.size_hint = [None, None]
        self.width = 900
        self.height = 1600
        self.add_widget(Label(text=text, text_size=(800, None)))


class MainWindow(Screen):
    first_half = True

    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = "main"

    def show_description(self, *args):
        if args[0].collide_point(args[1].x, args[1].y):
            LastPopup(args[0].children[1].text).open()

    def show_teacher(self, *args):
        if args[0].collide_point(args[1].x, args[1].y):
            index = mobi.lessons[1].index(args[0].children[0].text)

            lesson = args[0].children[1].text
            tab = ""
            found = False
            if lesson[0] == "[":
                for i in range(len(lesson)):
                    if not found:
                        if lesson[i] == "]":
                            found = True
                    else:
                        if lesson[i] != "(":
                            tab += lesson[i]
                        else:
                            break
                    i += 1
            else:
                for i in range(len(lesson)):
                    if lesson[i] != "(":
                        tab += lesson[i]
                    else:
                        break
            lesson = tab

            TeacherPopup(lesson, mobi.teachers[index]).open()

    def show_message(self, *args):
        if args[0].collide_point(args[1].x, args[1].y):
            index = mobi.message_titles.index(args[0].text)
            MessagePopup(
                f"{args[0].text} - {mobi.message_sender[index]}", mobi.messages[index]
            ).open()

    def change_half(self, *args):
        if args[0].collide_point(args[1].x, args[1].y):
            length = len(args[0].children) - 3
            if self.first_half:
                i = 0
                once = False
                self.first_half = False
                for parent in args[0].children:
                    if not once:
                        parent.children[0].text = mobi.avg2
                        once = True
                    elif i != 10:
                        try:
                            index = mobi.red_names2.index(
                                mobi.marks_avg_name[length - i]
                            )
                            parent.children[0].text = mobi.red_marks2[index]
                            parent.children[0].color = [1, 0, 0, 1]
                        except ValueError:
                            parent.children[0].text = mobi.marks_avg2[length - i]
                            parent.children[0].color = [1, 1, 1, 1]
                        i += 1
                    else:
                        parent.text = "Srednie ocen z przedmiotow z II okresu:"
            else:
                i = 0
                once = False
                self.first_half = True
                for parent in args[0].children:
                    if not once:
                        parent.children[0].text = mobi.avg
                        once = True
                    elif i != 10:
                        try:
                            index = mobi.red_names.index(
                                mobi.marks_avg_name[length - i]
                            )
                            parent.children[0].text = mobi.red_marks[index]
                            parent.children[0].color = [1, 0, 0, 1]
                        except ValueError:
                            parent.children[0].text = mobi.marks_avg[length - i]
                            parent.children[0].color = [1, 1, 1, 1]
                        i += 1
                    else:
                        parent.text = "Srednie ocen z przedmiotow z I okresu:"

    def on_pre_enter(self, *args):
        try:
            carousel = Carousel(direction="right", loop=True)
            box_main = BoxLayout(orientation="vertical")
            last_label = Label(text="Ostatnie oceny:", bold=True, font_size=55)
            box_main.add_widget(last_label)
            for i in range(len(mobi.last_marks)):
                last_box = BoxLayout(
                    orientation="horizontal", on_touch_down=self.show_description
                )
                name_label = Label(
                    text=str(mobi.last_marks_name[i]),
                    text_size=(600, 200),
                    valign="center",
                    halign="right",
                )
                mark_label = Label(
                    text=str(mobi.last_marks[i]), text_size=(None, 200), valign="center"
                )
                last_box.add_widget(name_label)
                last_box.add_widget(mark_label)
                box_main.add_widget(last_box)
            if len(mobi.last_marks) < 3:
                box_main.add_widget(Widget())

            box_marks = BoxLayout(
                orientation="vertical",
                on_touch_down=self.change_half,
                size_hint_y=None,
                height=1400,
            )

            marks_avg_label = Label(
                text="Srednie ocen z przedmiotow z I okresu:", bold=True, font_size=55
            )
            box_marks.add_widget(marks_avg_label)

            for i in range(len(mobi.marks_avg_name)):
                mark_avg_box = BoxLayout(orientation="horizontal")
                name_label = Label(
                    text=str(mobi.marks_avg_name[i]),
                    text_size=(600, 200),
                    valign="center",
                    halign="right",
                )
                try:
                    index = mobi.red_names.index(mobi.marks_avg_name[i])
                    mark_avg_label = Label(
                        text=str(mobi.red_marks[index]), color=[1, 0, 0, 1]
                    )
                except ValueError:
                    mark_avg_label = Label(text=str(mobi.marks_avg[i]))
                mark_avg_box.add_widget(name_label)
                mark_avg_box.add_widget(mark_avg_label)
                box_marks.add_widget(mark_avg_box)
            avg_box = BoxLayout(orientation="horizontal")
            avg_name_label = Label(
                text="Srednia polroczna:",
                text_size=(600, 200),
                valign="center",
                halign="right",
                bold=True,
            )
            avg_label = Label(text=str(mobi.avg))
            avg_box.add_widget(avg_name_label)
            avg_box.add_widget(avg_label)

            box_marks.add_widget(avg_box)
            box_main.add_widget(box_marks)
            carousel.add_widget(box_main)
            timetable = BoxLayout(orientation="vertical")
            timetable.add_widget(
                Label(text=f"[b]{mobi.lessons[2]}[/b]", markup=True, font_size=55)
            )
            for i, j in zip(mobi.lessons[0], mobi.lessons[1]):
                lh = BoxLayout(
                    orientation="horizontal", on_touch_down=self.show_teacher
                )
                lh.add_widget(
                    Label(
                        text=str(i),
                        markup=True,
                        text_size=(500, 200),
                        valign="center",
                        halign="right",
                    )
                )
                lh.add_widget(Label(text=str(j), markup=True))
                timetable.add_widget(lh)
            carousel.add_widget(timetable)
            mess_box = BoxLayout(orientation="vertical")
            mess_box.add_widget(
                Label(text="[b]Wiadomości:[/b]", font_size=55, markup=True)
            )
            for i in range(len(mobi.message_titles)):
                mess_box.add_widget(
                    Label(text=mobi.message_titles[i], on_touch_down=self.show_message)
                )
            carousel.add_widget(mess_box)
            exam_box = BoxLayout(orientation="vertical")
            exam_box.add_widget(
                Label(text="[b]Sprawdziany:[/b]", markup=True, font_size=55)
            )
            for i in mobi.exams:
                exam_cont = BoxLayout(orientation="horizontal")
                exam_cont.add_widget(
                    Label(text=str(i[0]), text_size=(350, None), halign="right")
                )
                exam_cont.add_widget(
                    Label(text=str(i[1]), text_size=(350, None), halign="center")
                )
                exam_cont.add_widget(Label(text=str(i[2]), text_size=(350, None)))
                exam_box.add_widget(exam_cont)
            homework_box = BoxLayout(orientation="vertical")
            homework_box.add_widget(
                Label(text="[b]Zadania domowe:[/b]", markup=True, font_size=55)
            )
            for i in mobi.homeworks:
                homework_cont = BoxLayout(orientation="horizontal")
                homework_cont.add_widget(
                    Label(text=str(i[0]), text_size=(350, None), halign="right")
                )
                homework_cont.add_widget(
                    Label(text=str(i[1]), text_size=(350, None), halign="center")
                )
                homework_cont.add_widget(Label(text=str(i[2]), text_size=(350, None)))
                homework_box.add_widget(homework_cont)
            container = BoxLayout(orientation="vertical")
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
        box_main = BoxLayout(orientation="vertical", padding=50, spacing=100)
        web_box = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=70, pos_hint={"top": 1}
        )
        web_label = Label(text="Adres:")
        self.web_url = TextInput(multiline=False, size_hint_x=None, width=250)
        web_end = Label(text=".mobidziennik.pl", size_hint_x=None, width=400)
        web_box.add_widget(web_label)
        web_box.add_widget(self.web_url)
        web_box.add_widget(web_end)
        login_box = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=70, pos_hint={"top": 1}
        )
        login_label = Label(text="Login:")
        self.login_input = TextInput(multiline=False)
        login_box.add_widget(login_label)
        login_box.add_widget(self.login_input)

        password_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=70)
        password_label = Label(text="Haslo:")
        self.password_input = TextInput(multiline=False, password=True)
        password_box.add_widget(password_label)
        password_box.add_widget(self.password_input)
        box_main.add_widget(web_box)
        box_main.add_widget(login_box)
        box_main.add_widget(password_box)

        sign_button = Button(
            text="Zaloguj", on_press=self.sign, size_hint_y=None, height=140
        )
        box_main.add_widget(sign_button)
        box_main.add_widget(Widget())
        self.add_widget(box_main)

    def sign(self, *args):
        try:
            data = {"login": self.login_input.text, "haslo": self.password_input.text}
            web_url = self.web_url.text
            web = requests.post(
                f"https://{web_url}.mobidziennik.pl/mobile/glowna", data=data
            )
            if (
                web.url
                == f"https://mobidziennik.pl/zlyadres.php?adres={web_url}.mobidziennik.pl"
            ):
                ErrorPopup("Podano zły adres!").open()
            else:
                tree = html.fromstring(web.content)
                test = tree.xpath('//div[@id="p-login-info-text"]/text()')
                if not test:
                    asyncio.get_event_loop().run_until_complete(
                        asyncio.gather(
                            get_last_marks(mobi, data, web_url),
                            get_first_marks(mobi, data, web_url),
                            get_second_marks(mobi, data, web_url),
                            get_timetables(mobi, data, web_url),
                            get_exams(mobi, data, web_url),
                            get_homeworks(mobi, data, web_url),
                            get_messages(mobi, data, web_url),
                        )
                    )
                    key = Fernet.generate_key()
                    with open("mobi.b", "wb") as file:
                        file.write(key)
                        file.write(b"\n")
                        f = Fernet(key)
                        login = data.get("login")
                        login = login.encode()
                        login = f.encrypt(login)
                        password = data.get("haslo")
                        password = password.encode()
                        password = f.encrypt(password)
                        web_url = web_url.encode()
                        web_url = f.encrypt(web_url)
                        file.write(login)
                        file.write(b"\n")
                        file.write(password)
                        file.write(b"\n")
                        file.write(web_url)
                    self.parent.current = "main"
                else:
                    ErrorPopup("Podano błędne dane logowania").open()
        except UnicodeError:
            ErrorPopup("Adres nie może być pusty").open()
        except Exception as e:
            ErrorPopup(str(e)).open()


class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(SignInWindow())
        self.add_widget(MainWindow())
        if mobi.isFile:
            self.current = "main"


class MobiMain(App):
    def build(self):
        return WindowManager(transition=FadeTransition())


mobi_main = MobiMain()
mobi_main.run()
