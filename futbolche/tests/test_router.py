import importlib
from unittest import mock

from test_support import BasePatchedTestCase


class TestRouter(BasePatchedTestCase):
    def setUp(self):
        self.router = importlib.import_module('chatbot.router')

    def test_handle_intent_status_logging(self):
        with mock.patch('chatbot.router._route', return_value='ok'), \
             mock.patch('chatbot.router.log_command') as log_command:
            self.assertEqual(self.router.handle_intent('help', None, 'raw'), 'ok')
            log_command.assert_called_with('raw', 'help', 'OK', 'ok')
        with mock.patch('chatbot.router._route', return_value='Грешка при нещо'), \
             mock.patch('chatbot.router.log_command') as log_command:
            self.router.handle_intent('help', None, 'raw')
            log_command.assert_called_with('raw', 'help', 'ERROR', 'Грешка при нещо')

    def test_help_exit_and_unknown(self):
        intents = [{'tag': 'add_club', 'examples': ['добави клуб [club_name]']}]
        with mock.patch('chatbot.router._load_intents', return_value=intents):
            text = self.router._route('help', None)
            self.assertIn('Клубове:', text)
            self.assertIn('добави клуб', text)
        self.assertEqual(self.router._route('exit', None), 'exit')
        self.assertIn('Не разбирам', self.router._route('unknown', None))

    def test_match_handler_routes(self):
        with mock.patch('chatbot.router.handle_show_round', return_value='round'):
            self.assertEqual(self.router._route('show_round', {}), 'round')
        with mock.patch('chatbot.router.handle_show_events', return_value='events'):
            self.assertEqual(self.router._route('show_events', {}), 'events')
        with mock.patch('chatbot.router.handle_predict_match', return_value='pred'):
            self.assertEqual(self.router._route('predict_match', {}), 'pred')

    def test_club_routes(self):
        self.assertIn('Името не може', self.router._route('add_club', None))
        with mock.patch('chatbot.router.add_club', return_value='added'):
            self.assertEqual(self.router._route('add_club', {'club_name': 'A'}), 'added')
        with mock.patch('chatbot.router.get_all_clubs', return_value='clubs'):
            self.assertEqual(self.router._route('list_clubs', None), 'clubs')
        self.assertIn('Укажете име', self.router._route('delete_club', None))
        with mock.patch('chatbot.router.delete_club', return_value='deleted'):
            self.assertEqual(self.router._route('delete_club', {'club_name': 'A'}), 'deleted')
        self.assertEqual(self.router._route('update_club', None), 'Невалидни параметри.')
        self.assertIn('Формат', self.router._route('update_club', {'club_name': 'A'}))
        with mock.patch('chatbot.router.update_club', return_value='updated'):
            self.assertEqual(self.router._route('update_club', {'club_name': 'A', 'new_name': 'B'}), 'updated')

    def test_league_routes(self):
        self.assertIn('Недостатъчни параметри', self.router._route('create_league', None))
        with mock.patch('chatbot.router.leagues.create_league', return_value='created'):
            self.assertEqual(self.router._route('create_league', {'league_name': 'A', 'season': '2025'}), 'created')
        self.assertIn('Недостатъчни параметри', self.router._route('add_club_to_league', None))
        with mock.patch('chatbot.router.leagues.add_club_to_league', return_value='added'):
            self.assertEqual(self.router._route('add_club_to_league', {'league_identifier': 'L', 'club_identifier': 'C'}), 'added')
        self.assertIn('Формат', self.router._route('remove_club_from_league', None))
        with mock.patch('chatbot.router.leagues.remove_club_from_league', return_value='removed'):
            self.assertEqual(self.router._route('remove_club_from_league', {'league_identifier': 'L', 'club_identifier': 'C'}), 'removed')
        self.assertIn('Формат', self.router._route('get_league_teams', None))
        with mock.patch('chatbot.router.leagues.get_league_teams', return_value=[]):
            self.assertIn('няма отбори', self.router._route('get_league_teams', {'league_identifier': 'L'}).lower())
        with mock.patch('chatbot.router.leagues.get_league_teams', return_value=[{'name': 'A', 'id': 1}]):
            self.assertIn('ID: 1', self.router._route('get_league_teams', {'league_identifier': 'L'}))
        self.assertIn('Формат', self.router._route('generate_round_robin', None))
        with mock.patch('chatbot.router.leagues.generate_round_robin', return_value='round robin'):
            self.assertEqual(self.router._route('generate_round_robin', {'league_identifier': 'L'}), 'round robin')
        self.assertIn('Формат', self.router._route('get_fixtures', None))
        with mock.patch('chatbot.router.leagues.get_fixtures', return_value='fixtures'):
            self.assertEqual(self.router._route('get_fixtures', {'league_identifier': 'L'}), 'fixtures')

    def test_player_routes(self):
        self.assertIn('Недостатъчни параметри', self.router._route('add_player', None))
        with mock.patch('chatbot.router.players.get_club_id', return_value=None):
            self.assertIn('не съществува', self.router._route('add_player', {'full_name': 'P', 'club_identifier': 'C'}))
        with mock.patch('chatbot.router.players.get_club_id', return_value=1), \
             mock.patch('chatbot.router.players.add_player', return_value='added'):
            self.assertEqual(self.router._route('add_player', {'full_name': 'P', 'club_identifier': 'C'}), 'added')
        with mock.patch('chatbot.router.players.get_players_by_club', return_value='players'):
            self.assertEqual(self.router._route('list_players', {'club_identifier': 'C'}), 'players')
            self.assertEqual(self.router._route('list_players', None), 'players')
            self.assertEqual(self.router._route('list_all_players', None), 'players')
        self.assertIn('Недостатъчни параметри', self.router._route('update_player_position', None))
        with mock.patch('chatbot.router.players.update_player_position', return_value='ok'):
            self.assertEqual(self.router._route('update_player_position', {'player_identifier': 'P', 'new_position': 'GK'}), 'ok')
        self.assertIn('Недостатъчни параметри', self.router._route('update_player_number', None))
        with mock.patch('chatbot.router.players.update_player_number', return_value='ok'):
            self.assertEqual(self.router._route('update_player_number', {'player_identifier': 'P', 'new_number': '9'}), 'ok')
        self.assertIn('Недостатъчни параметри', self.router._route('update_player_status', None))
        with mock.patch('chatbot.router.players.update_player_status', return_value='ok'):
            self.assertEqual(self.router._route('update_player_status', {'player_identifier': 'P', 'new_status': 'Активен'}), 'ok')
        self.assertIn('Укажете играч', self.router._route('delete_player', None))
        with mock.patch('chatbot.router.players.delete_player', return_value='deleted'):
            self.assertEqual(self.router._route('delete_player', {'player_identifier': 'P'}), 'deleted')

    def test_statistics_routes(self):
        self.assertIn('Недостатъчни параметри', self.router._route('club_statistics', None))
        with mock.patch('chatbot.router.stats.get_club_statistics', return_value=None):
            self.assertIn('не съществува', self.router._route('club_statistics', {'club_identifier': 'C'}))
        with mock.patch('chatbot.router.stats.get_club_statistics', return_value={'played': 1, 'wins': 1, 'draws': 0, 'losses': 0, 'goals_for': 2, 'goals_against': 1, 'goal_difference': 1, 'points': 3}):
            self.assertIn('Статистика за клуб', self.router._route('club_statistics', {'club_identifier': 'C'}))
        self.assertIn('Недостатъчни параметри', self.router._route('player_statistics', None))
        with mock.patch('chatbot.router.stats.get_player_statistics', return_value=None):
            self.assertIn('не съществува', self.router._route('player_statistics', {'player_identifier': 'P'}))
        with mock.patch('chatbot.router.stats.get_player_statistics', return_value={'goals': 1, 'assists': 2, 'appearances': 3, 'yellow_cards': 4, 'red_cards': 0}):
            self.assertIn('Статистика за играч', self.router._route('player_statistics', {'player_identifier': 'P'}))
        self.assertIn('Недостатъчни параметри', self.router._route('player_metrics', None))
        with mock.patch('chatbot.router.stats.get_player_advanced_metrics', return_value=None):
            self.assertIn('не съществува', self.router._route('player_metrics', {'player_identifier': 'P'}))
        with mock.patch('chatbot.router.stats.get_player_advanced_metrics', return_value={'minutes_played': 90, 'goals_per_90': 1.0, 'assists_per_90': 0.5}):
            self.assertIn('Разширени метрики', self.router._route('player_metrics', {'player_identifier': 'P'}))

    def test_record_match_and_event_routes(self):
        self.assertIn('Недостатъчни параметри', self.router._route('record_match', None))
        with mock.patch('chatbot.router.matches.record_match', return_value='match saved'):
            self.assertEqual(self.router._route('record_match', {'home_team': 'A'}), 'match saved')
        self.assertIn('Формат', self.router._route('show_match', None))
        with mock.patch('chatbot.router.matches.get_match', return_value=None):
            self.assertIn('не е намерен', self.router._route('show_match', {'match_id': '1'}))
        with mock.patch('chatbot.router.matches.get_match', return_value={'match_date': '2025-01-01', 'home_name': 'A', 'away_name': 'B', 'home_goals': 1, 'away_goals': 0}):
            self.assertEqual(self.router._route('show_match', {'match_id': '1'}), '2025-01-01: A 1-0 B')
        self.assertIn('Недостатъчни параметри', self.router._route('record_event', None))
        with mock.patch('chatbot.router.players.get_player_id', return_value=None):
            self.assertIn('не съществува', self.router._route('record_event', {'match_id': '1', 'event_type': 'goal', 'player_identifier': 'P'}))
        with mock.patch('chatbot.router.players.get_player_id', return_value=1), \
             mock.patch('repositories.players_repo.get_by_id', return_value=None):
            self.assertIn('няма клуб', self.router._route('record_event', {'match_id': '1', 'event_type': 'goal', 'player_identifier': 'P'}))
        with mock.patch('chatbot.router.players.get_player_id', return_value=1), \
             mock.patch('repositories.players_repo.get_by_id', return_value={'club_id': 2}), \
             mock.patch('chatbot.router.matches.record_event', return_value='recorded'):
            self.assertIn('цяло число', self.router._route('record_event', {'match_id': 'bad', 'event_type': 'goal', 'player_identifier': 'P'}))
            self.assertEqual(self.router._route('record_event', {'match_id': '1', 'event_type': 'goal', 'player_identifier': 'P'}), 'recorded')

    def test_remaining_routes(self):
        with mock.patch('chatbot.router.handle_show_standings', return_value='standings'):
            self.assertEqual(self.router._route('get_standings', {}), 'standings')
        self.assertIn('Недостатъчни параметри', self.router._route('show_transfers_player', None))
        with mock.patch('chatbot.router.transfers.list_transfers_by_player', return_value='player transfers'):
            self.assertEqual(self.router._route('show_transfers_player', {'player_identifier': 'P'}), 'player transfers')
        self.assertIn('Недостатъчни параметри', self.router._route('show_transfers_club', None))
        with mock.patch('chatbot.router.transfers.list_transfers_by_club', return_value='club transfers'):
            self.assertEqual(self.router._route('show_transfers_club', {'club_identifier': 'C'}), 'club transfers')
        self.assertIn('Недостатъчни параметри', self.router._route('transfer_player', None))
        self.assertIn('Недостатъчни параметри', self.router._route('transfer_player', {'player_identifier': 'P'}))
        with mock.patch('chatbot.router.transfers.transfer_player', return_value='transfer ok'):
            self.assertEqual(self.router._route('transfer_player', {'player_identifier': 'P', 'club_identifier': 'C'}), 'transfer ok')
