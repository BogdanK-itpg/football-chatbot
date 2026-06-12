import importlib
import types
from unittest import mock

from test_support import BasePatchedTestCase


class FakeVar:
    def __init__(self, value=None):
        self.value = value
        self.callbacks = []

    def get(self):
        return self.value

    def set(self, value):
        self.value = value

    def trace_add(self, *_args):
        self.callbacks.append(True)


class FakeWidget:
    def __init__(self):
        self.bound = []

    def pack(self, *args, **kwargs):
        return None

    def bind(self, *args, **kwargs):
        self.bound.append((args, kwargs))


class FakeFrame:
    def __init__(self):
        self.children = []

    def winfo_children(self):
        return list(self.children)

    def columnconfigure(self, *_args, **_kwargs):
        return None


class FakePreview:
    def __init__(self):
        self.text = ''

    def config(self, *args, **kwargs):
        return None

    def delete(self, *_args, **_kwargs):
        self.text = ''

    def insert(self, *_args):
        self.text = _args[-1]


class TestCommandBuilderUi(BasePatchedTestCase):
    def setUp(self):
        self.mod = importlib.import_module('commands.command_builder_ui')
        self.CommandNode = importlib.import_module('commands.command_tree').CommandNode

    def _make_panel(self):
        panel = self.mod.CommandBuilderPanel.__new__(self.mod.CommandBuilderPanel)
        panel._tree_builder = mock.Mock()
        panel._tree = self.CommandNode('root', 'Команди', 'root')
        panel._current_node = None
        panel._on_execute = mock.Mock()
        panel._param_widgets = {}
        panel._scroll_frame = FakeFrame()
        panel._breadcrumb = mock.Mock()
        panel._back_btn = mock.Mock()
        panel._execute_btn = mock.Mock()
        panel._preview_text = FakePreview()
        panel._clear_options = self.mod.CommandBuilderPanel._clear_options.__get__(panel, self.mod.CommandBuilderPanel)
        panel._update_breadcrumb = self.mod.CommandBuilderPanel._update_breadcrumb.__get__(panel, self.mod.CommandBuilderPanel)
        panel._show_node = self.mod.CommandBuilderPanel._show_node.__get__(panel, self.mod.CommandBuilderPanel)
        panel._show_children_as_buttons = self.mod.CommandBuilderPanel._show_children_as_buttons.__get__(panel, self.mod.CommandBuilderPanel)
        panel._show_parameter_form = self.mod.CommandBuilderPanel._show_parameter_form.__get__(panel, self.mod.CommandBuilderPanel)
        panel._get_var = self.mod.CommandBuilderPanel._get_var.__get__(panel, self.mod.CommandBuilderPanel)
        panel._get_ptype = self.mod.CommandBuilderPanel._get_ptype.__get__(panel, self.mod.CommandBuilderPanel)
        panel._collect_params = self.mod.CommandBuilderPanel._collect_params.__get__(panel, self.mod.CommandBuilderPanel)
        panel._build_intent_dict = self.mod.CommandBuilderPanel._build_intent_dict.__get__(panel, self.mod.CommandBuilderPanel)
        panel._update_preview = self.mod.CommandBuilderPanel._update_preview.__get__(panel, self.mod.CommandBuilderPanel)
        panel._go_back = self.mod.CommandBuilderPanel._go_back.__get__(panel, self.mod.CommandBuilderPanel)
        panel._execute = self.mod.CommandBuilderPanel._execute.__get__(panel, self.mod.CommandBuilderPanel)
        panel.reset = self.mod.CommandBuilderPanel.reset.__get__(panel, self.mod.CommandBuilderPanel)
        return panel

    def test_show_node_children_and_forms(self):
        panel = self._make_panel()
        command = self.CommandNode('cmd_test', 'Test', 'command', metadata={'tag': 'test', 'example': 'пример'})
        command.add_child(self.CommandNode('param_name', 'Име', 'parameter', metadata={'param_name': 'name', 'param_type': 'TEXT', 'required': True, 'enum_values': []}))
        root = panel._tree
        root.add_child(command)

        fake_button = FakeWidget()
        fake_label = FakeWidget()
        with mock.patch.object(self.mod.tk, 'Button', return_value=fake_button), \
             mock.patch.object(self.mod.tk, 'Label', return_value=fake_label), \
             mock.patch.object(self.mod.ttk, 'Label', return_value=fake_label):
            panel._show_children_as_buttons(root)
            self.assertEqual(panel._back_btn.config.call_args.kwargs['state'], self.mod.tk.DISABLED)

        no_param_cmd = self.CommandNode('cmd_empty', 'Empty', 'command', metadata={'tag': 'empty'})
        with mock.patch.object(self.mod.ttk, 'Label', return_value=fake_label):
            panel._show_parameter_form(no_param_cmd)
            panel._execute_btn.config.assert_called()

    def test_parameter_form_widget_types_and_collection(self):
        panel = self._make_panel()
        command = self.CommandNode('cmd_test', 'Test', 'command', metadata={'tag': 'test'})
        command.children = [
            self.CommandNode('p_enum', 'Enum', 'parameter', metadata={'param_name': 'event_type', 'param_type': 'ENUM', 'required': True, 'enum_values': ['goal']}),
            self.CommandNode('p_int', 'Int', 'parameter', metadata={'param_name': 'minute', 'param_type': 'INTEGER', 'required': True, 'enum_values': []}),
            self.CommandNode('p_float', 'Float', 'parameter', metadata={'param_name': 'fee', 'param_type': 'FLOAT', 'required': False, 'enum_values': []}),
            self.CommandNode('p_bool', 'Bool', 'parameter', metadata={'param_name': 'flag', 'param_type': 'BOOLEAN', 'required': False, 'enum_values': []}),
            self.CommandNode('p_text_opts', 'TextOpts', 'parameter', metadata={'param_name': 'club_identifier', 'param_type': 'TEXT', 'required': True, 'enum_values': []}),
            self.CommandNode('p_text', 'Text', 'parameter', metadata={'param_name': 'full_name', 'param_type': 'TEXT', 'required': False, 'enum_values': []}),
        ]

        fake_label = FakeWidget()
        fake_combo = FakeWidget()
        fake_spin = FakeWidget()
        fake_entry = FakeWidget()
        fake_check = FakeWidget()

        with mock.patch.object(self.mod.ttk, 'Label', return_value=fake_label), \
             mock.patch.object(self.mod.ttk, 'Combobox', return_value=fake_combo), \
             mock.patch.object(self.mod.ttk, 'Spinbox', return_value=fake_spin), \
             mock.patch.object(self.mod.tk, 'Entry', return_value=fake_entry), \
             mock.patch.object(self.mod.ttk, 'Checkbutton', return_value=fake_check), \
             mock.patch.object(self.mod.tk, 'StringVar', side_effect=[FakeVar(), FakeVar(), FakeVar(), FakeVar(), FakeVar()]), \
             mock.patch.object(self.mod.tk, 'BooleanVar', return_value=FakeVar(False)), \
             mock.patch('commands.command_builder_ui.get_options_for_param', side_effect=[ [('Club', 'Club')], [] ]):
            panel._show_parameter_form(command)

        panel._param_widgets['event_type']['var'].set('goal')
        panel._param_widgets['minute']['var'].set('23')
        panel._param_widgets['fee']['var'].set('150000')
        panel._param_widgets['flag']['var'].set(True)
        panel._param_widgets['club_identifier']['var'].set('Club')
        panel._param_widgets['full_name']['var'].set('Иван Иванов')
        params = panel._collect_params()
        self.assertEqual(params['event_type'], 'goal')
        self.assertEqual(params['flag'], 'true')
        self.assertEqual(params['club_identifier'], 'Club')
        self.assertEqual(panel._get_ptype(panel._param_widgets['minute']), 'INTEGER')

    def test_build_preview_execute_and_navigation(self):
        panel = self._make_panel()
        root = panel._tree
        command = self.CommandNode('cmd_test', 'Test', 'command', metadata={'tag': 'test'})
        command.add_child(self.CommandNode('p1', 'Name', 'parameter', metadata={'param_name': 'full_name', 'required': True}))
        root.add_child(command)
        command.parent = root
        panel._current_node = command
        panel._param_widgets = {
            'full_name': {'var': FakeVar('Иван Иванов'), 'ptype': 'TEXT', 'options_map': {}}
        }
        self.assertEqual(panel._build_intent_dict(), {'intent': 'test', 'parameters': {'full_name': 'Иван Иванов'}})
        panel._update_preview()
        self.assertIn('Иван Иванов', panel._preview_text.text)
        with mock.patch.object(self.mod.tk, 'Button', return_value=FakeWidget()), \
             mock.patch.object(self.mod.tk, 'Label', return_value=FakeWidget()):
            panel._go_back()

        panel._current_node = None
        self.assertIsNone(panel._build_intent_dict())
        with mock.patch.object(panel, '_build_intent_dict', return_value=None):
            with mock.patch('commands.command_builder_ui.messagebox.showwarning') as warning:
                panel._execute()
                warning.assert_called_once()

        panel._current_node = command
        panel._param_widgets = {}
        panel._execute()
        panel._on_execute.assert_called_with('test', None)

        command.add_child(self.CommandNode('p2', 'Optional', 'parameter', metadata={'param_name': 'note', 'required': False}))
        panel._current_node = command
        panel._param_widgets = {
            'full_name': {'var': FakeVar(''), 'ptype': 'TEXT', 'options_map': {}},
            'note': {'var': FakeVar('filled'), 'ptype': 'TEXT', 'options_map': {}},
        }
        with mock.patch('commands.command_builder_ui.messagebox.showwarning') as warning:
            panel._execute()
            warning.assert_called_once()

        panel._param_widgets = {'full_name': {'var': FakeVar('Иван'), 'ptype': 'TEXT', 'options_map': {}}}
        panel._execute()
        panel._on_execute.assert_called_with('test', {'full_name': 'Иван'})

        with mock.patch.object(self.mod.tk, 'Button', return_value=FakeWidget()), \
             mock.patch.object(self.mod.tk, 'Label', return_value=FakeWidget()):
            panel.reset()
            self.assertEqual(panel._current_node, root)
