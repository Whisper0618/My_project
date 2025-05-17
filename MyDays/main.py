from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.properties import NumericProperty
from datetime import date
import calendar
from functools import partial
from kivy.graphics import Rectangle, Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.metrics import dp, sp
from kivy.utils import platform
from kivy.core.window import Window
from kivy.clock import Clock  # ✅ 针对长按检测
from kivy.storage.jsonstore import JsonStore
from kivy.core.text import LabelBase

LabelBase.register(name="ChineseFont", fn_regular="fonts/NotoSansSC-Regular.ttf")


Window.clearcolor = (1, 1, 1, 1)  # 设置整个窗口背景为白色


class MainScreen(Screen):
    current_year = NumericProperty(date.today().year)
    current_month = NumericProperty(date.today().month)

    long_press_event = None
    long_press_detected = False
    popup_open = False

    def open_edit_task_popup(self, original_text, on_save_callback):
        popup = Popup(
            title='Edit Task',
            size_hint=(0.85, 0.5),
            auto_dismiss=True
        )

        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        input_field = TextInput(
            text=original_text,
            multiline=True,
            size_hint=(1, None),
            height=dp(150),
            font_size=sp(16),
            foreground_color=(0.2, 0.2, 0.2, 1),
            halign='left',
            cursor_width=1,
            cursor_color=(0.2, 0.2, 0.2, 1),
            padding=[dp(10), dp(10), dp(10), dp(10)],
            write_tab=False
        )

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(input_field)

        save_btn = Button(text='Save', font_size=sp(14), size_hint_y=None, height=dp(40))

        def save_content(_):
            new_text = input_field.text.strip()
            if new_text:
                on_save_callback(new_text)
            popup.dismiss()

        save_btn.bind(on_release=save_content)
        content.add_widget(scroll)
        content.add_widget(save_btn)
        popup.content = content
        popup.open()

    def on_kv_post(self, base_widget):
        """当 KV 文件加载完成后，初始化日历。"""
        self.update_calendar()

    def update_calendar(self):
        """刷新日历网格。"""
        self.ids.calendar_title.text = f"{calendar.month_name[self.current_month]} {self.current_year}"
        self.ids.calendar_grid.clear_widgets()
        today = date.today()
        cal = calendar.Calendar(firstweekday=6)

        # 创建星期标题行
        for day in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
            self.ids.calendar_grid.add_widget(Button(
                text=day,
                font_size=sp(12),
                disabled=True,
                background_normal='',
                background_color=(0.95, 0.95, 0.95, 1),
                color=(0.3, 0.3, 0.3, 1),
                size_hint=(None, None),
                width=dp(40),
                height=dp(40)
            ))

        for week in cal.monthdayscalendar(self.current_year, self.current_month):
            for d in week:
                if d == 0:
                    # 空白日期，用一个空 BoxLayout 占位
                    self.ids.calendar_grid.add_widget(BoxLayout(
                        size_hint=(None, None),
                        size=(dp(40), dp(50))
                    ))
                else:
                    # 检查是否该日有待办任务
                    has_todo = App.get_running_app().check_has_todo(self.current_year, self.current_month, d)

                    # 外层 box 可以承载更多组件（如数字、标记等）
                    date_box = BoxLayout(
                        orientation='vertical',
                        spacing=dp(4),
                        size_hint=(None, None),
                        size=(dp(40), dp(50))
                    )

                    # 日期按钮
                    btn = Button(
                        text=str(d),
                        font_size=sp(12),
                        size_hint=(1, None),
                        height=dp(40),
                        background_normal='',
                        background_color=(1, 1, 1, 1),
                        color=(0, 0, 0, 1)
                    )
                    # 如果是当天则红色高亮
                    if (self.current_year == today.year and
                        self.current_month == today.month and
                        d == today.day):
                        btn.background_color = (1, 0.7, 0.7, 1)
                    elif has_todo:
                        btn.background_color = (0.95, 0.9, 0.8, 1)

                    # 绑定点击长按事件
                    btn.bind(on_touch_down=partial(self.on_date_touch_down, d))
                    btn.bind(on_touch_up=partial(self.on_date_touch_up, d))

                    date_box.add_widget(btn)
                    self.ids.calendar_grid.add_widget(date_box)

    def on_date_touch_down(self, day, btn, touch):
        """检测触摸按下事件，用于识别长按。"""
        if not btn.collide_point(*touch.pos):
            return
        self.long_press_detected = False

        def do_long_press(dt):
            self.long_press_detected = True
            self.long_press_event = None  # 避免重复触发
            App.get_running_app().switch_screen('todo')
            App.get_running_app().open_add_task_popup(
                prefill=f"Task on {self.current_year}-{self.current_month:02d}-{day:02d}: "
            )

        # 0.5秒长按
        try:
            self.long_press_event = Clock.schedule_once(do_long_press, 0.5)
        except Exception as e:
            print("⛔ 长按处理失败:", e)

    def on_date_touch_up(self, day, btn, touch):
        """检测触摸抬起事件，若非长按则弹窗显示任务清单。"""
        # 取消长按计时器
        if self.long_press_event:
            self.long_press_event.cancel()
            self.long_press_event = None

        if self.long_press_detected:
            # 已经长按了就不弹窗
            return

        if btn.collide_point(*touch.pos):
            self.show_tasks_popup_for_day(day)

    def _trigger_long_press(self, day):
        """可选的直接手动触发长按逻辑。"""
        if self.long_press_event:
            self.long_press_event = None
            self.long_press_detected = True
            App.get_running_app().switch_screen('todo')
            App.get_running_app().open_add_task_popup(
                prefill=f"Task on {self.current_year}-{self.current_month:02d}-{day:02d}: "
            )

    def show_tasks_popup_for_day(self, day):
        """弹窗显示某天的任务列表。"""
        if self.popup_open:
            return
        self.popup_open = True

        # 先保存一下 todo 数据，以防忘记
        App.get_running_app().save_todo_data()
        app = App.get_running_app()
        store = app.store
        tasks = []

        target_prefix = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
        if store.exists("todo_tasks"):
            for task in store.get("todo_tasks")['items']:
                if target_prefix in task.get('text', ''):
                    tasks.append(task['text'])

        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        scroll = ScrollView(size_hint=(1, 1))
        task_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        task_layout.bind(minimum_height=task_layout.setter('height'))

        # 将每个任务/提示添加到布局
        if tasks:
            # 将每个任务/提示添加到布局
            # 将每个任务/提示添加到布局
            if tasks:
                for t in tasks:
                    wrapper = BoxLayout(size_hint_y=None, padding=dp(5))

                    label = Label(
                        text=t if len(t) <= 40 else t[:40] + "...",
                        font_size=sp(14),
                        size_hint_y=None,
                        size_hint_x=1,
                        halign='left',
                        valign='top',
                        shorten=False,
                        color=(1, 1, 1, 1)
                    )
                    label.full_text = t

                    def on_label_touch(instance, touch):
                        if instance.collide_point(*touch.pos):
                            def save_callback(new_text):
                                # 修改对应 task_list 中的 label.full_text 并保存
                                todo_screen = App.get_running_app().sm.get_screen("todo")
                                for task_box in todo_screen.ids.task_list.children:
                                    label = getattr(task_box, "label", None)
                                    if label and label.full_text == instance.full_text:
                                        label.text = new_text[:40] + "..." if len(new_text) > 40 else new_text
                                        label.full_text = new_text
                                        break
                                App.get_running_app().save_todo_data()
                                App.get_running_app().sm.get_screen("calendar").update_calendar()

                            self.open_edit_task_popup(instance.full_text, save_callback)

                    label.bind(
                        width=lambda inst, val: setattr(inst, 'text_size', (val, None)),
                        texture_size=lambda inst, val: setattr(inst, 'height', val[1]),
                        on_touch_down=on_label_touch  # ✅ 改为独立函数绑定
                    )

                    wrapper.add_widget(label)
                    task_layout.add_widget(wrapper)



            else:
                label = Label(
                    text="No tasks.",
                    font_size=sp(14),
                    size_hint_y=None,
                    halign='left',
                    valign='top',
                    color=(1, 1, 1, 0.6)
                )
                label.bind(
                    width=lambda inst, val: setattr(inst, 'text_size', (val, None)),
                    texture_size=lambda inst, val: setattr(inst, 'height', val[1])
                )
                task_layout.add_widget(label)

            scroll.add_widget(task_layout)
            content.add_widget(scroll)

        popup = Popup(
            title=f"Tasks on {target_prefix}",
            title_size=sp(16),
            content=content,
            size_hint=(0.85, 0.6)
        )

        def reset_flag(*args):
            self.popup_open = False

        popup.bind(on_dismiss=reset_flag)
        popup.open()

    def next_month(self):
        """下个月按钮。"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_calendar()

    def prev_month(self):
        """上个月按钮。"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_calendar()


class ToDoScreen(Screen):
    def add_task(self, task_text, is_done=None):
        if not task_text.strip():
            return

        display_text = task_text if len(task_text) <= 40 else task_text[:40] + "..."

        task_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(80),
            spacing=dp(10),
            padding=dp(10)
        )
        with task_box.canvas.before:
            Color(1, 0.98, 0.94, 1)
            task_box.bg = RoundedRectangle(pos=task_box.pos, size=task_box.size, radius=[dp(20)])
        task_box.bind(pos=lambda inst, val: setattr(task_box.bg, 'pos', val))
        task_box.bind(size=lambda inst, val: setattr(task_box.bg, 'size', val))

        checkbox_layout = BoxLayout(size_hint=(None, 1), width=dp(40))
        checkbox_anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        checkbox = CheckBox(size_hint=(None, None), size=(dp(30), dp(30)))
        checkbox.active = is_done if is_done is not None else False
        checkbox.bind(active=lambda inst, value: App.get_running_app().save_todo_data())
        checkbox_anchor.add_widget(checkbox)
        checkbox_layout.add_widget(checkbox_anchor)

        label = Label(
            text=display_text,
            halign='left',
            valign='top',
            size_hint_x=1,
            text_size=(0, None),
            font_size=sp(14),
            color=(0.2, 0.2, 0.2, 1)
        )
        label.full_text = task_text  # ✅ 保存完整原文
        label.bind(
            size=lambda inst, val: setattr(inst, 'text_size', inst.size),
            on_touch_down=lambda inst, touch: self.show_full_task(inst.full_text, inst)
            if inst.collide_point(*touch.pos) else None
        )

        delete_btn = Button(
            background_normal='icon6.png',
            background_down='icon6.png',
            background_color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            on_release=lambda x: self.remove_task(task_box)
        )
        with delete_btn.canvas.before:
            Color(1, 1, 1, 1)
            delete_btn.bg = RoundedRectangle(pos=delete_btn.pos, size=delete_btn.size, radius=[dp(20)])
        delete_btn.bind(pos=lambda inst, val: setattr(delete_btn.bg, 'pos', val))
        delete_btn.bind(size=lambda inst, val: setattr(delete_btn.bg, 'size', val))

        task_box.add_widget(checkbox_layout)
        task_box.add_widget(label)
        task_box.add_widget(delete_btn)
        task_box.checkbox = checkbox
        task_box.label = label

        self.ids.task_list.add_widget(task_box)
        App.get_running_app().save_todo_data()

        calendar_screen = App.get_running_app().sm.get_screen('calendar')
        calendar_screen.update_calendar()

    def remove_task(self, task_widget):
        """移除某个任务。"""
        self.ids.task_list.remove_widget(task_widget)
        app = App.get_running_app()
        app.save_todo_data()

        # 同步刷新 Calendar
        calendar_screen = app.sm.get_screen('calendar')
        calendar_screen.update_calendar()

    def show_full_task(self, original_text, label_widget):
        popup = Popup(
            title='Edit Task',
            size_hint=(0.85, 0.5),
            auto_dismiss=True
        )

        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        input_field = TextInput(
            text=original_text,
            multiline=True,
            size_hint=(1, None),
            height=dp(150),
            font_size=sp(16),
            foreground_color=(0.2, 0.2, 0.2, 1),
            halign='left',
            cursor_width=1,
            cursor_color=(0.2, 0.2, 0.2, 1),
            padding=[dp(10), dp(10), dp(10), dp(10)],
            write_tab=False
        )

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(input_field)

        save_btn = Button(text='Save', font_size=sp(14), size_hint_y=None, height=dp(40))

        def save_content(_):
            new_text = input_field.text.strip()
            label_widget.text = (new_text[:40] + '...') if len(new_text) > 40 else new_text
            label_widget.full_text = new_text

            app = App.get_running_app()
            app.save_todo_data()  # ✅ 强制保存

            # ✅ 强制刷新日历（更新任务标记）
            if hasattr(app, "sm") and app.sm.has_screen("calendar"):
                app.sm.get_screen("calendar").update_calendar()

            popup.dismiss()

        save_btn.bind(on_release=save_content)
        content.add_widget(scroll)
        content.add_widget(save_btn)
        popup.content = content
        popup.open()


class CourseScreen(Screen):
    def on_enter(self):
        """进入Course页时，如果课程设置没配，就弹窗设置，否则直接生成表格。"""
        app = App.get_running_app()
        if not app.course_configured:
            app.open_course_settings_popup()
        else:
            app.generate_course_grid(app.course_days, app.course_periods)


class NotesScreen(Screen):
    def add_note(self, note_text):
        """添加新笔记。"""
        if not note_text.strip():
            return

        display_text = note_text if len(note_text) <= 50 else note_text[:50] + "..."

        note_wrapper = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(80),
            padding=dp(10),
            spacing=dp(10)
        )
        with note_wrapper.canvas.before:
            Color(1, 0.98, 0.94, 1)
            note_wrapper.bg = RoundedRectangle(pos=note_wrapper.pos, size=note_wrapper.size, radius=[dp(20)])
        note_wrapper.bind(pos=lambda inst, val: setattr(note_wrapper.bg, 'pos', val))
        note_wrapper.bind(size=lambda inst, val: setattr(note_wrapper.bg, 'size', val))

        note_label = Label(
            text=display_text,
            halign='left',
            valign='top',
            size_hint_x=0.85,
            font_size=sp(14),
            text_size=(0, None),
            color=(0.2, 0.2, 0.2, 1)
        )
        note_label.bind(
            size=lambda inst, val: setattr(inst, 'text_size', inst.size),
            on_touch_down=lambda inst, touch: self.show_full_note(note_text) if inst.collide_point(*touch.pos) else None
        )

        delete_btn = Button(
            background_normal='icon6.png',
            background_down='icon6.png',
            background_color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            on_release=lambda x: self.remove_note(note_wrapper)
        )
        with delete_btn.canvas.before:
            Color(1, 1, 1, 1)
            delete_btn.bg = RoundedRectangle(pos=delete_btn.pos, size=delete_btn.size, radius=[dp(20)])
        delete_btn.bind(pos=lambda inst, val: setattr(delete_btn.bg, 'pos', val))
        delete_btn.bind(size=lambda inst, val: setattr(delete_btn.bg, 'size', val))

        note_wrapper.label = note_label
        note_wrapper.add_widget(note_label)
        note_wrapper.add_widget(delete_btn)

        self.ids.notes_list.add_widget(note_wrapper)
        App.get_running_app().save_notes_data()

    def remove_note(self, note_widget):
        """删除笔记。"""
        self.ids.notes_list.remove_widget(note_widget)
        App.get_running_app().save_notes_data()

    def open_add_note_popup(self):
        """添加笔记的弹窗。"""
        popup = Popup(title='Add Note', size_hint=(0.85, 0.4))
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        note_input = TextInput(
            hint_text='Enter your note...',
            multiline=True,
            font_size=sp(14)
        )
        add_btn = Button(text='Save', font_size=sp(14), size_hint_y=None, height=dp(40))

        def save_note(_):
            self.add_note(note_input.text)
            popup.dismiss()

        add_btn.bind(on_release=save_note)
        content.add_widget(note_input)
        content.add_widget(add_btn)
        popup.content = content
        popup.open()

    def show_full_note(self, note_text):
        """查看笔记内容的弹窗，支持滚动。"""
        popup = Popup(title='', size_hint=(0.85, 0.6), background='', separator_height=0)
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        # 背景
        with content.canvas.before:
            Color(1, 1, 1, 1)
            content.bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[dp(20)])
        content.bind(pos=lambda inst, val: setattr(content.bg, 'pos', val))
        content.bind(size=lambda inst, val: setattr(content.bg, 'size', val))

        label = Label(
            text=note_text,
            font_size=sp(16),
            color=(0.2, 0.2, 0.2, 1),
            halign='left',
            valign='top',
            size_hint_y=None,
            text_size=(Window.width * 0.7, None)
        )
        label.bind(texture_size=lambda inst, val: setattr(inst, 'height', val[1]))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(label)
        content.add_widget(scroll)
        popup.content = content
        popup.open()


class MyScreenManager(ScreenManager):
    """用来管理各个 Screen 的切换。"""
    pass


class MyApp(App):
    """主应用类。"""
    course_configured = False
    course_days = None
    course_periods = None


    course_time_inputs = []
    course_cells = []

    def build(self):
        import os
        self.store = JsonStore(os.path.join(self.user_data_dir, "settings.json"))


        root_layout = BoxLayout(orientation='vertical')

        # 屏幕管理器
        self.sm = MyScreenManager()
        self.sm.add_widget(MainScreen(name='calendar'))
        self.sm.add_widget(ToDoScreen(name='todo'))
        self.sm.add_widget(CourseScreen(name='course'))
        self.sm.add_widget(NotesScreen(name='notes'))
        root_layout.add_widget(self.sm)

        # 底部按钮栏
        button_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(100),
            spacing=dp(10),
            padding=[dp(10), 0]
        )

        # 左侧留白
        button_bar.add_widget(Widget(size_hint_x=2))

        # 几个页面按钮
        buttons = [
            ('icon1.png', 'Calendar', 'calendar'),
            ('icon2.png', 'To Do', 'todo'),
            ('icon3.png', 'Course', 'course'),
            ('icon4.png', 'Notes', 'notes')
        ]

        for i, (icon, label, screen) in enumerate(buttons):
            btn = BoxLayout(orientation='vertical', size_hint=(None, 1), width=dp(60), spacing=dp(4))
            # 图标按钮
            btn.add_widget(Button(
                background_normal=icon,
                size_hint=(None, None),
                size=(dp(60), dp(60)),
                on_release=partial(self.switch_screen, screen)
            ))
            # 文字按钮
            btn.add_widget(Button(
                text=label,
                font_size=sp(12),
                background_normal='',
                color=(0.2, 0.2, 0.2, 1),
                size_hint=(None, None),
                size=(dp(60), dp(20))
            ))
            button_bar.add_widget(btn)

            # 中间的空Widget分隔
            if i != len(buttons) - 1:
                button_bar.add_widget(Widget(size_hint_x=1))

        # 右侧留白
        button_bar.add_widget(Widget(size_hint_x=2))

        # 背景米色
        with button_bar.canvas.before:
            Color(252 / 255, 247 / 255, 241 / 255, 1)  # (#FCF7F1)
            self.bg_rect = Rectangle(pos=button_bar.pos, size=button_bar.size)
        button_bar.bind(pos=self._update_bg, size=self._update_bg)

        root_layout.add_widget(button_bar)
        return root_layout

    def _update_bg(self, instance, *args):
        """更新底部 bar 的背景矩形大小和位置。"""
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def switch_screen(self, screen_name, *args):
        """切换页面。"""
        self.sm.current = screen_name

    def open_add_task_popup(self, prefill=""):
        """弹窗添加新的待办任务。"""
        popup = Popup(title='Add Task', size_hint=(0.8, 0.3))
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        task_input = TextInput(
            text=prefill,
            hint_text='Enter your task here',
            multiline=False,
            font_size=sp(14)
        )
        add_btn = Button(text='Add', font_size=sp(14), size_hint_y=None, height=dp(40))

        def on_add(_):
            self.sm.get_screen('todo').add_task(task_input.text)
            popup.dismiss()

        add_btn.bind(on_release=on_add)
        content.add_widget(task_input)
        content.add_widget(add_btn)
        popup.content = content
        popup.open()

    def open_course_settings_popup(self):
        """弹窗：设置课程表的天数与节数。"""
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

        layout.add_widget(Label(text="Periods per day:", font_size=sp(18), size_hint_y=None, height=dp(30)))
        periods_spinner = Spinner(
            text="6 periods",
            values=[f"{i} periods" for i in range(1, 11)],
            size_hint=(1, None),
            height=dp(40)
        )
        layout.add_widget(periods_spinner)

        layout.add_widget(Label(text="Days per week:", font_size=sp(18), size_hint_y=None, height=dp(30)))
        days_spinner = Spinner(
            text="Mon–Fri",
            values=["Mon–Fri", "Mon–Sat", "Sun–Sat", "Mon–Sun"],
            size_hint=(1, None),
            height=dp(40)
        )
        layout.add_widget(days_spinner)

        save_btn = Button(text="Save Settings", font_size=sp(16), size_hint_y=None, height=dp(50))
        layout.add_widget(save_btn)

        popup = Popup(title="Schedule Settings", title_size=sp(16), content=layout, size_hint=(0.9, 0.6))

        def save_settings(_):
            days_dict = {"Mon–Fri": 5, "Mon–Sat": 6, "Sun–Sat": 7, "Mon–Sun": 7}
            self.course_days = days_dict[days_spinner.text]
            self.course_periods = int(periods_spinner.text.split()[0])
            self.course_configured = True
            self.store.put("course", days=self.course_days, periods=self.course_periods)
            popup.dismiss()
            self.generate_course_grid(self.course_days, self.course_periods)

        save_btn.bind(on_release=save_settings)
        popup.open()

    def generate_course_grid(self, days, periods):
        """根据设置的天数和节数生成课程表格。"""
        screen = self.sm.get_screen('course')
        grid = screen.ids.course_grid
        grid.clear_widgets()
        grid.cols = days + 1
        grid.rows = periods + 1

        self.course_time_inputs = []
        self.course_cells = []
        # 创建外部滚动视图
        scroll_view = ScrollView(size_hint=(1, None), height=dp(600))  # 设置ScrollView的高度
        grid_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        grid_layout.bind(minimum_height=grid_layout.setter('height'))
        # 第一行：Time + weekday
        grid.add_widget(Label(text='Time', bold=True, color=(0, 0, 0, 1), font_size=sp(14)))
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for j in range(days):
            grid.add_widget(Label(text=weekdays[j], bold=True, color=(0, 0, 0, 1), font_size=sp(14)))

        # 后续 rows: 每一行是一节课
        for i in range(periods):
            time_input = TextInput(
                hint_text="e.g. 08:00",
                multiline=False,
                size_hint_y=None,
                height=dp(80),
                font_size=sp(14)
            )
            time_input.bind(focus=lambda inst, foc: self.save_course_data() if not foc else None)
            self.course_time_inputs.append(time_input)
            grid.add_widget(time_input)

            row_cells = []
            for j in range(days):
                course_input = TextInput(
                    multiline=False,
                    size_hint_y=None,
                    height=dp(80),
                    font_size=sp(14)
                )
                course_input.bind(focus=lambda inst, foc: self.save_course_data() if not foc else None)
                row_cells.append(course_input)
                grid.add_widget(course_input)
            self.course_cells.append(row_cells)

        self.load_course_data()

    def load_course_data(self):
        """从存储加载课程表内容。"""
        if self.store.exists("course_contents"):
            data = self.store.get("course_contents")
            stored_times = data.get("times", [])
            stored_cells = data.get("cells", [])
            for i in range(min(len(self.course_time_inputs), len(stored_times))):
                self.course_time_inputs[i].text = stored_times[i]
            for i in range(min(len(self.course_cells), len(stored_cells))):
                row_data = stored_cells[i]
                for j in range(min(len(self.course_cells[i]), len(row_data))):
                    self.course_cells[i][j].text = row_data[j]

    def save_course_data(self):
        """保存课程表内容。"""
        times = [t.text for t in self.course_time_inputs]
        cells = [[c.text for c in row] for row in self.course_cells]
        self.store.put("course_contents", times=times, cells=cells)

    def check_has_todo(self, year, month, day):
        """检查指定日期是否有 Todo 任务。"""
        if not self.store.exists("todo_tasks"):
            return False
        items = self.store.get("todo_tasks")['items']
        target_prefix = f"{year}-{month:02d}-{day:02d}"
        for task in items:
            if target_prefix in task.get('text', ''):
                return True
        return False

    def save_todo_data(self):
        tasks = []
        task_list = self.sm.get_screen('todo').ids.task_list.children[::-1]
        for task_box in task_list:
            tasks.append({
                'text': task_box.label.full_text,  # ✅ 保存完整文本而不是显示文本
                'done': task_box.checkbox.active
            })
        self.store.put("todo_tasks", items=tasks)

    def load_todo_data(self):
        """加载待办列表。"""
        if self.store.exists("todo_tasks"):
            items = self.store.get("todo_tasks")['items']
            todo_screen = self.sm.get_screen('todo')
            for task in items:
                if isinstance(task, dict):
                    # 新格式（含 done 状态）
                    todo_screen.add_task(task['text'], is_done=task.get('done', False))
                else:
                    # 旧格式（纯文本）
                    todo_screen.add_task(task, is_done=False)

    def save_notes_data(self):
        """存储笔记列表。"""
        notes = []
        notes_list = self.sm.get_screen('notes').ids.notes_list.children[::-1]
        for note_box in notes_list:
            if hasattr(note_box, 'label'):
                notes.append(note_box.label.text)
        self.store.put("notes_data", items=notes)

    def load_notes_data(self):
        """加载笔记列表。"""
        if self.store.exists("notes_data"):
            items = self.store.get("notes_data")['items']
            print("🔁 Loaded notes:", items)
            notes_screen = self.sm.get_screen('notes')
            for note in items:
                notes_screen.add_note(note)

    def on_back_button(self, window, key, *args):
        """安卓设备的返回键处理：回到 calendar，若已在 calendar 就交给系统。"""
        if key == 27:  # ESC / Android back
            if self.sm.current != 'calendar':
                self.sm.current = 'calendar'
                return True
        return False

    def on_start(self):
        if platform == 'android':
            Window.bind(on_keyboard=self.on_back_button)

        if self.store.exists("course"):
            info = self.store.get("course")
            self.course_days = info.get("days")
            self.course_periods = info.get("periods")
            self.course_configured = True

            # 延迟加载，避免 UI 渲染阻塞
        Clock.schedule_once(lambda dt: self.load_todo_data(), 0.1)
        Clock.schedule_once(lambda dt: self.load_notes_data(), 0.2)


if __name__ == '__main__':
    MyApp().run()