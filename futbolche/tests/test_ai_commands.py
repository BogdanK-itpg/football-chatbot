import importlib
import os
import runpy
import tempfile
import types
from unittest import mock

from test_support import BasePatchedTestCase, SRC_ROOT


class TestAiAndCommandModules(BasePatchedTestCase):
    def test_ai_commands_tree_intent_schema_and_logger(self):
        probability = importlib.import_module('ai.probability')
        features = importlib.import_module('ai.features')
        ai_service = importlib.import_module('ai.ai_service')
        intent_schema = importlib.import_module('commands.intent_schema')
        command_tree = importlib.import_module('commands.command_tree')
        data_provider = importlib.import_module('commands.data_provider')
        logger = importlib.import_module('utils.logger')
        chatbot = importlib.import_module('chatbot.chatbot')

        self.assertGreater(probability.calculate_team_index({'form': 1, 'attack': 1, 'defense': 1, 'ranking': 1}), 0)
        self.assertEqual(probability.calculate_draw_probability(10, 0), 0.15)
        probs = probability.calculate_probabilities({'form': 0, 'attack': 0, 'defense': 0, 'ranking': 0}, {'form': 0, 'attack': 0, 'defense': 0, 'ranking': 0})
        self.assertEqual(sum(probs.values()), 100)
        probs2 = probability.calculate_probabilities({'form': 1, 'attack': 1, 'defense': 1, 'ranking': 1}, {'form': 0.5, 'attack': 0.5, 'defense': 0.5, 'ranking': 0.5})
        self.assertEqual(sum(probs2.values()), 100)

        with mock.patch('ai.features.matches_repo.get_all', return_value=[]):
            self.assertEqual(features.get_last_matches(1), [])
            self.assertEqual(features.calculate_form(1), 0.0)
            self.assertEqual(features.calculate_attack_strength(1), 0.0)
            self.assertEqual(features.calculate_defense_strength(1), 0.0)
        with mock.patch('ai.features.matches_repo.get_all', return_value=[
            {'is_played': 1, 'home_goals': 2, 'away_goals': 1, 'home_team_id': 1, 'away_team_id': 2, 'match_date': '2025-01-01'},
            {'is_played': 1, 'home_goals': 0, 'away_goals': 0, 'home_team_id': 2, 'away_team_id': 1, 'match_date': '2025-01-02'},
        ]):
            self.assertEqual(len(features.get_last_matches(1)), 2)
            self.assertGreater(features.calculate_form(1), 0)
            self.assertGreater(features.calculate_attack_strength(1), 0)
            self.assertGreater(features.calculate_defense_strength(1), 0)
        with mock.patch('ai.features.leagues_repo.get_by_id', return_value=None):
            self.assertEqual(features.calculate_ranking_score(1, 1), 0.0)
        with mock.patch('ai.features.leagues_repo.get_by_id', return_value={'name': 'A', 'season': '2025'}), \
             mock.patch('ai.features.calculate_standings', return_value=[]):
            self.assertEqual(features.calculate_ranking_score(1, 1), 0.0)
        with mock.patch('ai.features.leagues_repo.get_by_id', return_value={'name': 'A', 'season': '2025'}), \
             mock.patch('ai.features.calculate_standings', return_value=[{'team_id': 1, 'position': 2}, {'team_id': 2, 'position': 1}]):
            self.assertEqual(features.calculate_ranking_score(1, 1), 0.5)
        with mock.patch('ai.features.leagues_repo.get_by_id', return_value={'name': 'A', 'season': '2025'}), \
             mock.patch('ai.features.calculate_standings', return_value=[{'team_id': 2, 'position': 1}]):
            self.assertEqual(features.calculate_ranking_score(1, 1), 0.0)
        with mock.patch('ai.features.calculate_form', return_value=1), \
             mock.patch('ai.features.calculate_attack_strength', return_value=2), \
             mock.patch('ai.features.calculate_defense_strength', return_value=3), \
             mock.patch('ai.features.calculate_ranking_score', return_value=4):
            self.assertEqual(features.build_team_features(1, 2)['ranking'], 4)
            self.assertEqual(features.build_team_features(1)['ranking'], 0.0)

        with mock.patch('ai.ai_service.clubs_repo.get_by_name', return_value=None):
            self.assertIsNone(ai_service._get_team_id('A'))
            with self.assertRaises(ValueError):
                ai_service.predict_match('A', 'B')
        with mock.patch('ai.ai_service.clubs_repo.get_by_name', side_effect=[{'id': 1}, {'id': 2}]), \
             mock.patch('ai.ai_service.leagues_repo.get_all', return_value=[]):
            self.assertIsNone(ai_service._find_common_league(1, 2))
            with self.assertRaises(ValueError):
                ai_service.predict_match('A', 'B')
        with mock.patch('ai.ai_service.clubs_repo.get_by_name', side_effect=[{'id': 1}, {'id': 2}]), \
             mock.patch('ai.ai_service.leagues_repo.get_all', return_value=[{'id': 1}]), \
             mock.patch('ai.ai_service.leagues_repo.get_teams', return_value=[{'id': 1}, {'id': 2}]), \
             mock.patch('ai.ai_service.features.get_last_matches', side_effect=[[1], [1]]):
            with self.assertRaises(ValueError):
                ai_service.predict_match('A', 'B')
        with mock.patch('ai.ai_service.clubs_repo.get_by_name', side_effect=[{'id': 1}, {'id': 2}]), \
             mock.patch('ai.ai_service.leagues_repo.get_all', return_value=[{'id': 1}]), \
             mock.patch('ai.ai_service.leagues_repo.get_teams', return_value=[{'id': 1}, {'id': 2}]), \
             mock.patch('ai.ai_service.features.get_last_matches', side_effect=[[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]]), \
             mock.patch('ai.ai_service.features.build_team_features', side_effect=[{'form': 1, 'attack': 1, 'defense': 1, 'ranking': 1}, {'form': 1, 'attack': 1, 'defense': 1, 'ranking': 1}]), \
             mock.patch('ai.ai_service.probability.calculate_probabilities', return_value={'home': 33, 'draw': 33, 'away': 34}):
            self.assertEqual(ai_service.predict_match('A', 'B')['home'], 33)

        self.assertEqual(intent_schema.infer_param_type('position').name, 'ENUM')
        self.assertEqual(intent_schema.infer_param_type('home_goals').name, 'INTEGER')
        self.assertEqual(intent_schema.infer_param_type('match_date').name, 'DATE')
        self.assertEqual(intent_schema.infer_param_type('season').name, 'SEASON')
        self.assertEqual(intent_schema.infer_param_type('fee').name, 'FLOAT')
        self.assertEqual(intent_schema.infer_param_type('name').name, 'TEXT')
        self.assertEqual(intent_schema._extract_params_from_patterns(['x [a] [b]']), {'a': True, 'b': True})
        self.assertIn('Име на клуба', intent_schema._generate_param_hint('club_name'))
        self.assertEqual(intent_schema._intent_tag_to_label('unknown_tag'), 'Unknown Tag')
        self.assertTrue(intent_schema._param_is_optional_in_patterns('season', ['x [id] [season]', 'x [id]']))
        self.assertTrue(intent_schema._param_is_optional_for_intent('record_event', 'minute', []))
        built = intent_schema.build_intent_schema({'tag': 'record_event', 'patterns': ['запиши [event_type] [player_identifier] в мач [match_id] минута [minute]'], 'responses': ['r'], 'examples': ['e']}, 'Мачове')
        self.assertEqual(built.tag, 'record_event')
        self.assertEqual(built.category, 'Мачове')
        self.assertTrue(any(p.name == 'match_id' for p in built.parameters))
        self.assertEqual(intent_schema.ParameterDef('x').to_dict()['name'], 'x')
        self.assertEqual(intent_schema.IntentSchema('t', 'l', []).to_dict()['tag'], 't')

        node = command_tree.CommandNode('a', 'A', 'root')
        child = command_tree.CommandNode('b', 'B', 'child')
        child2 = command_tree.CommandNode('c', 'C', 'child')
        node.add_child(child)
        node.add_child(child2)
        self.assertEqual(node.find('b'), child)
        self.assertIsNone(node.find('x'))
        self.assertEqual([n.id for n in child.path_from_root()], ['a', 'b'])
        builder = command_tree.CommandTreeBuilder()
        self.assertIsInstance(builder.get_all_schemas(), dict)
        self.assertIsNone(builder.get_schema('missing'))
        self.assertEqual(builder._find_category('help'), 'Други')
        self.assertIn('Други', builder.get_intents_by_category())
        root = builder.build_tree()
        self.assertEqual(root.label, 'Команди')
        with mock.patch('commands.command_tree.open', side_effect=OSError('boom')):
            builder2 = command_tree.CommandTreeBuilder()
            self.assertEqual(builder2.get_all_schemas(), {})

        self.assertEqual(data_provider.get_options_for_param(''), [])
        with mock.patch('commands.data_provider._get_from_club_options', return_value=[('x', 'y')]):
            self.assertEqual(data_provider.get_options_for_param('from_club'), [('x', 'y')])
        with mock.patch('commands.data_provider._get_club_options', return_value=[('x', 'y')]):
            self.assertEqual(data_provider.get_options_for_param('home_team'), [('x', 'y')])
            self.assertEqual(data_provider.get_options_for_param('club_identifier'), [('x', 'y')])
        with mock.patch('commands.data_provider._get_player_options', return_value=[('x', 'y')]):
            self.assertEqual(data_provider.get_options_for_param('player_identifier'), [('x', 'y')])
        with mock.patch('commands.data_provider._get_league_options', return_value=[('x', 'y')]):
            self.assertEqual(data_provider.get_options_for_param('league_identifier'), [('x', 'y')])
        with mock.patch('commands.data_provider._get_match_options', return_value=[('x', 'y')]):
            self.assertEqual(data_provider.get_options_for_param('match_id'), [('x', 'y')])
        with mock.patch('commands.data_provider._get_season_options', return_value=[('x', 'y')]):
            self.assertEqual(data_provider.get_options_for_param('season'), [('x', 'y')])
        self.assertEqual(data_provider.get_options_for_param('unknown'), [])
        with mock.patch('commands.data_provider._get_club_options', return_value=[]):
            self.assertEqual(data_provider._get_from_club_options()[0], ('--- Свободен агент ---', 'няма'))
        import sys
        fake_repos = types.SimpleNamespace(
            clubs_repo=types.SimpleNamespace(get_all=lambda: [{'name': 'Club'}]),
            players_repo=types.SimpleNamespace(get_all=lambda: [{'full_name': 'P', 'club_name': None, 'number': None}]),
            leagues_repo=types.SimpleNamespace(get_all=lambda: [{'id': 1, 'name': 'L', 'season': '2025'}]),
            matches_repo=types.SimpleNamespace(get_all=lambda: [{'id': 1, 'home_name': 'A', 'away_name': 'B', 'is_played': 0, 'home_goals': None, 'away_goals': None, 'match_date': '2025-01-01'}]),
        )
        with mock.patch.dict(sys.modules, {'repositories': fake_repos}):
            self.assertEqual(data_provider._get_club_options(), [('Club', 'Club')])
            self.assertEqual(data_provider._get_player_options()[0][1], 'P')
            self.assertEqual(data_provider._get_league_options(), [('L (2025)', '1')])
            self.assertIn('#1 A ?:? B', data_provider._get_match_options()[0][0])
        fake_seasons = types.SimpleNamespace(leagues_repo=types.SimpleNamespace(get_all=lambda: [{'season': '2025'}, {'season': '2025/26'}]))
        with mock.patch.dict(sys.modules, {'repositories': fake_seasons}):
            self.assertEqual(data_provider._get_season_options(), [('2025', '2025'), ('2025/26', '2025/26')])
        failing_repos = types.SimpleNamespace(
            clubs_repo=types.SimpleNamespace(get_all=lambda: (_ for _ in ()).throw(Exception())),
            players_repo=types.SimpleNamespace(get_all=lambda: (_ for _ in ()).throw(Exception())),
            leagues_repo=types.SimpleNamespace(get_all=lambda: (_ for _ in ()).throw(Exception())),
            matches_repo=types.SimpleNamespace(get_all=lambda: (_ for _ in ()).throw(Exception())),
        )
        with mock.patch.dict(sys.modules, {'repositories': failing_repos}):
            self.assertEqual(data_provider._get_club_options(), [])
            self.assertEqual(data_provider._get_player_options(), [])
            self.assertEqual(data_provider._get_league_options(), [])
            self.assertEqual(data_provider._get_match_options(), [])
            self.assertEqual(data_provider._get_season_options(), [('2025', '2025')])

        with tempfile.TemporaryDirectory() as tmp:
            log_path = os.path.join(tmp, 'commands.log')
            with mock.patch('utils.logger.LOG_PATH', log_path):
                logger.log_command('raw', 'intent', 'OK', 'reason', {'a': 1})
            with open(log_path, 'r', encoding='utf-8') as f:
                self.assertIn('intent', f.read())
        with mock.patch('builtins.open', side_effect=OSError('nope')):
            logger.log_command('raw', 'intent', 'OK')

        with mock.patch('chatbot.chatbot.parse_input', return_value=('help', None)), \
             mock.patch('chatbot.chatbot.route_intent', return_value='ok'):
            self.assertEqual(chatbot.parse_and_handle('x'), 'ok')
            self.assertEqual(chatbot.parse_input_wrapper('x'), ('help', None))
            self.assertEqual(chatbot.handle_intent('help', None), 'ok')


class TestNluAndGui(BasePatchedTestCase):
    def test_nlu_and_gui_paths(self):
        nlu = importlib.import_module('chatbot.nlu')
        main_window = importlib.import_module('GUI.main_window')

        with mock.patch('chatbot.nlu.open', side_effect=OSError('x')):
            self.assertEqual(nlu._load_intents(), [])
        regex, groups = nlu._pattern_to_regex('запиши мач [home]-[away] дата [season]')
        self.assertEqual(groups, ['home', 'away', 'season'])
        self.assertIsNotNone(regex.match('запиши мач A-B дата 2025'))
        with mock.patch('chatbot.nlu._load_intents', return_value=[{'tag': 'help', 'patterns': ['помощ']}, {'tag': 'record_match', 'patterns': ['запиши мач [home] срещу [away] дата [match_date] резултат [hg]-[ag]']}]):
            self.assertEqual(nlu.parse_input('помощ'), ('help', None))
            tag, params = nlu.parse_input('запиши мач Левски срещу ЦСКА дата 2025-01-01 резултат 2-1')
            self.assertEqual(tag, 'record_match')
            self.assertEqual(params['home'], 'Левски')
        with mock.patch('chatbot.nlu._load_intents', return_value=[]):
            self.assertEqual(nlu.parse_input('x'), ('unknown', None))

        fake_root = mock.Mock()
        fake_root.quit = mock.Mock()
        fake_root.title = mock.Mock()
        fake_root.geometry = mock.Mock()
        fake_root.configure = mock.Mock()
        fake_root.mainloop = mock.Mock()
        app = main_window.FootballChatbotGUI.__new__(main_window.FootballChatbotGUI)
        app.root = fake_root
        app.chat_display = mock.Mock()
        app.chat_display.index.return_value = '2.0'
        app.input_entry = mock.Mock()
        app._builder = mock.Mock()
        app._setup_ui = mock.Mock()
        app._add_welcome_message = mock.Mock()
        with mock.patch('GUI.main_window.initialize_database'):
            main_window.FootballChatbotGUI.__init__(app, fake_root)
        app._add_message = mock.Mock()
        app.input_entry.get.return_value = ''
        app._on_send()
        app.input_entry.get.return_value = 'hello'
        app._process_input = mock.Mock()
        app._on_send()
        app._process_input.assert_called_with('hello')
        app._execute_quick_command('help')
        app._execute_quick_command('list_clubs')
        app._execute_quick_command('list_all_players')
        app._execute_quick_command('get_standings')
        app._execute_quick_command('custom')
        with mock.patch('GUI.main_window.handle_intent_router', return_value='exit'):
            app._on_builder_execute('help', {})
            fake_root.quit.assert_called()
        with mock.patch('GUI.main_window.handle_intent_router', return_value='ok'):
            app._on_builder_execute('help', {})
        with mock.patch('GUI.main_window.parse_input_nlu', return_value=('help', None)), \
             mock.patch('GUI.main_window.handle_intent_router', return_value='ok'):
            app._process_input('hello')
        with mock.patch('GUI.main_window.parse_input_nlu', return_value=('exit', None)), \
             mock.patch('GUI.main_window.handle_intent_router', return_value='exit'):
            app._process_input('bye')
        with mock.patch('GUI.main_window.parse_input_nlu', side_effect=RuntimeError('bad')), \
             mock.patch('GUI.main_window.log_command'):
            app._process_input('oops')
        app.chat_display.index.return_value = '1.0'
        app._add_message = main_window.FootballChatbotGUI._add_message.__get__(app, main_window.FootballChatbotGUI)
        app._add_message('You', 'hi')
        app._add_message('Bot', 'ID  Име\nrow')
        app._add_message('Bot', 'plain')
        with mock.patch('GUI.main_window.tk.Tk', return_value=fake_root), \
             mock.patch('GUI.main_window.FootballChatbotGUI') as gui_cls:
            main_window.main()
            gui_cls.assert_called_once()
        with mock.patch.dict('sys.modules', {'GUI.main_window': types.SimpleNamespace(main=lambda: 'ran')}):
            runpy.run_path(os.path.join(SRC_ROOT, 'main.py'), run_name='__main__')
