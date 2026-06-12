import importlib
from unittest import mock

from test_support import BasePatchedTestCase


class TestServiceAndHandlerModules(BasePatchedTestCase):
    def test_clubs_and_players_services(self):
        clubs = importlib.import_module('services.clubs_service')
        players = importlib.import_module('services.players_service')

        self.assertEqual(clubs.add_club(''), 'Името не може да бъде празно.')
        with mock.patch('services.clubs_service.clubs_repo.get_by_name', return_value={'id': 1}):
            self.assertEqual(clubs.add_club('A'), 'Клуб с това име вече съществува.')
        with mock.patch('services.clubs_service.clubs_repo.get_by_name', return_value=None), \
             mock.patch('services.clubs_service.clubs_repo.create', return_value=None):
            self.assertEqual(clubs.add_club('A'), 'Грешка при добавяне на клуба.')
        with mock.patch('services.clubs_service.clubs_repo.get_by_name', return_value=None), \
             mock.patch('services.clubs_service.clubs_repo.create', return_value=1):
            self.assertIn('добавен успешно', clubs.add_club(' A '))
        with mock.patch('services.clubs_service.clubs_repo.get_all', return_value=[]):
            self.assertEqual(clubs.get_all_clubs(), 'Няма добавени клубове.')
        with mock.patch('services.clubs_service.clubs_repo.get_all', return_value=[{'name': 'A'}, {'name': 'B'}]):
            self.assertIn('1. A', clubs.get_all_clubs())
        with mock.patch('services.clubs_service.clubs_repo.get_by_id', return_value=None), \
             mock.patch('services.clubs_service.clubs_repo.get_by_name', return_value=None):
            self.assertEqual(clubs.delete_club('x'), 'Няма такъв клуб.')
        with mock.patch('services.clubs_service.clubs_repo.get_by_name', return_value={'id': 1, 'name': 'A'}), \
             mock.patch('services.clubs_service.clubs_repo.delete', return_value=None):
            self.assertEqual(clubs.delete_club('A'), 'Грешка при изтриване на клуба.')
        with mock.patch('services.clubs_service.clubs_repo.get_by_name', return_value={'id': 1, 'name': 'A'}), \
             mock.patch('services.clubs_service.clubs_repo.delete', return_value=True):
            self.assertIn('изтрит', clubs.delete_club('A'))
        with mock.patch('services.clubs_service.clubs_repo.get_by_name', return_value=None):
            self.assertEqual(clubs.update_club('A', new_name='B'), 'Клубът не беше намерен.')
        with mock.patch('services.clubs_service.clubs_repo.get_by_name', return_value={'id': 1}):
            self.assertEqual(clubs.update_club('A'), 'Няма зададени промени.')
            self.assertEqual(clubs.update_club('A', new_founded_year='bad'), 'Невалидна година на основаване.')
        with mock.patch('services.clubs_service.clubs_repo.get_by_name', return_value={'id': 1}), \
             mock.patch('services.clubs_service.clubs_repo.update', return_value=None):
            self.assertEqual(clubs.update_club('A', new_name='B'), 'Грешка при обновяване на клуба.')
        with mock.patch('services.clubs_service.clubs_repo.get_by_name', return_value={'id': 1}), \
             mock.patch('services.clubs_service.clubs_repo.update', return_value=True):
            self.assertEqual(clubs.update_club('A', new_name='B'), 'Клубът беше успешно обновен.')

        self.assertTrue(players.validate_position('GK'))
        self.assertFalse(players.validate_position('BAD'))
        self.assertTrue(players.validate_number('10'))
        self.assertFalse(players.validate_number('100'))
        self.assertTrue(players.validate_birth_date('2000-01-01'))
        self.assertFalse(players.validate_birth_date('2099-01-01'))
        with mock.patch('services.players_service.clubs_repo.get_by_id', return_value={'id': 1}):
            self.assertEqual(players.get_club_id('1'), 1)
        with mock.patch('services.players_service.clubs_repo.get_by_id', return_value=None), \
             mock.patch('services.players_service.clubs_repo.get_by_name', return_value={'id': 2}):
            self.assertEqual(players.get_club_id('A'), 2)
        with mock.patch('services.players_service.players_repo.get_by_id', return_value={'id': 1}):
            self.assertEqual(players.get_player_id('1'), 1)
        with mock.patch('services.players_service.players_repo.get_by_id', return_value=None), \
             mock.patch('services.players_service.players_repo.get_by_name', return_value={'id': 2}):
            self.assertEqual(players.get_player_id('A'), 2)
        self.assertEqual(players.add_player(1, '', '2000-01-01', 'BG', 'GK', 1, 'A'), 'Името на играча не може да бъде празно.')
        self.assertIn('Невaлидна дата', players.add_player(1, 'A', 'bad', 'BG', 'GK', 1, 'A'))
        self.assertEqual(players.add_player(1, 'A', '2000-01-01', '', 'GK', 1, 'A'), 'Националността не може да бъде празна.')
        self.assertIn('Невaлидна позиция', players.add_player(1, 'A', '2000-01-01', 'BG', 'BAD', 1, 'A'))
        self.assertIn('Невaлиден номер', players.add_player(1, 'A', '2000-01-01', 'BG', 'GK', 100, 'A'))
        self.assertEqual(players.add_player(1, 'A', '2000-01-01', 'BG', 'GK', 1, ''), 'Статусът не може да бъде празен.')
        with mock.patch('services.players_service.clubs_repo.exists', return_value=False):
            self.assertIn('не съществува', players.add_player(1, 'A', '2000-01-01', 'BG', 'GK', 1, 'A'))
        with mock.patch('services.players_service.clubs_repo.exists', return_value=True), \
             mock.patch('services.players_service.players_repo.exists_by_name_club', return_value=True):
            self.assertIn('вече съществува', players.add_player(1, 'A', '2000-01-01', 'BG', 'GK', 1, 'A'))
        with mock.patch('services.players_service.clubs_repo.exists', return_value=True), \
             mock.patch('services.players_service.players_repo.exists_by_name_club', return_value=False), \
             mock.patch('services.players_service.players_repo.create', return_value=None):
            self.assertIn('Грешка при добавяне', players.add_player(1, 'A', '2000-01-01', 'BG', 'GK', 1, 'A'))
        with mock.patch('services.players_service.clubs_repo.exists', return_value=True), \
             mock.patch('services.players_service.players_repo.exists_by_name_club', return_value=False), \
             mock.patch('services.players_service.players_repo.create', return_value=1):
            self.assertIn('добавен успешно', players.add_player(1, 'A', '2000-01-01', 'BG', 'GK', 1, 'A'))
        with mock.patch('services.players_service.players_repo.get_all', return_value=[]):
            self.assertEqual(players.get_players_by_club(), 'Няма намерени играчи.')
        with mock.patch('services.players_service.get_club_id', return_value=None):
            self.assertIn('не съществува', players.get_players_by_club('A'))
        with mock.patch('services.players_service.get_club_id', return_value=1), \
             mock.patch('services.players_service.players_repo.get_by_club', return_value=[{'id': 1, 'full_name': 'A', 'club_name': 'Club', 'position': 'GK', 'number': 1, 'nationality': 'BG', 'birth_date': '2000-01-01', 'status': 'Активен'}]):
            self.assertIn('ID', players.get_players_by_club('A'))
        self.assertIn('Невалидна позиция', players.update_player_position('A', 'BAD'))
        with mock.patch('services.players_service.get_player_id', return_value=None):
            self.assertIn('не съществува', players.update_player_position('A', 'GK'))
        with mock.patch('services.players_service.get_player_id', return_value=1), \
             mock.patch('services.players_service.players_repo.update', return_value=None):
            self.assertIn('Грешка', players.update_player_position('A', 'GK'))
        with mock.patch('services.players_service.get_player_id', return_value=1), \
             mock.patch('services.players_service.players_repo.update', return_value=True):
            self.assertIn('обновена', players.update_player_position('A', 'GK'))
        self.assertIn('Невалиден номер', players.update_player_number('A', '100'))
        with mock.patch('services.players_service.get_player_id', return_value=None):
            self.assertIn('не съществува', players.update_player_number('A', '9'))
        with mock.patch('services.players_service.get_player_id', return_value=1), \
             mock.patch('services.players_service.players_repo.update', return_value=None):
            self.assertIn('Грешка', players.update_player_number('A', '9'))
        with mock.patch('services.players_service.get_player_id', return_value=1), \
             mock.patch('services.players_service.players_repo.update', return_value=True):
            self.assertIn('сменен', players.update_player_number('A', '9'))
        self.assertEqual(players.update_player_status('A', ''), 'Статусът не може да бъде празен.')
        with mock.patch('services.players_service.get_player_id', return_value=None):
            self.assertIn('не съществува', players.update_player_status('A', 'Активен'))
        with mock.patch('services.players_service.get_player_id', return_value=1), \
             mock.patch('services.players_service.players_repo.update', return_value=None):
            self.assertIn('Грешка', players.update_player_status('A', 'Активен'))
        with mock.patch('services.players_service.get_player_id', return_value=1), \
             mock.patch('services.players_service.players_repo.update', return_value=True):
            self.assertIn('обновен', players.update_player_status('A', 'Активен'))
        with mock.patch('services.players_service.get_player_id', return_value=None):
            self.assertIn('не съществува', players.delete_player('A'))
        with mock.patch('services.players_service.get_player_id', return_value=1), \
             mock.patch('services.players_service.players_repo.delete', return_value=None):
            self.assertIn('Грешка', players.delete_player('A'))
        with mock.patch('services.players_service.get_player_id', return_value=1), \
             mock.patch('services.players_service.players_repo.delete', return_value=True):
            self.assertIn('изтрит', players.delete_player('A'))

    def test_statistics_matches_leagues_transfers_and_handlers(self):
        statistics = importlib.import_module('services.statistics_service')
        matches = importlib.import_module('services.matches_service')
        leagues = importlib.import_module('services.leagues_service')
        transfers = importlib.import_module('services.transfers_service')
        standings = importlib.import_module('services.standings_service')
        h_ai = importlib.import_module('handlers.handler_ai')
        h_matches = importlib.import_module('handlers.handler_matches')
        h_standings = importlib.import_module('handlers.handler_standings')

        with mock.patch('services.statistics_service._resolve_club_id', return_value=None):
            self.assertIsNone(statistics.get_club_statistics('A'))
        with mock.patch('services.statistics_service._resolve_club_id', return_value=1), \
             mock.patch('services.statistics_service.matches_repo.get_by_league', return_value=[]), \
             mock.patch('services.statistics_service.matches_repo.get_all', return_value=[
                 {'home_team_id': 1, 'away_team_id': 2, 'home_goals': 2, 'away_goals': 1},
                 {'home_team_id': 3, 'away_team_id': 1, 'home_goals': 1, 'away_goals': 1},
                 {'home_team_id': 1, 'away_team_id': 4, 'home_goals': None, 'away_goals': None},
             ]):
            club_stats = statistics.get_club_statistics('A')
            self.assertEqual(club_stats['played'], 2)
            self.assertEqual(club_stats['wins'], 1)
            self.assertEqual(club_stats['draws'], 1)
        with mock.patch('services.statistics_service._resolve_player_id', return_value=None):
            self.assertIsNone(statistics.get_player_statistics('A'))
        with mock.patch('services.statistics_service._resolve_player_id', return_value=1), \
             mock.patch('services.statistics_service.events_repo.count_by_player', side_effect=[2, 3, 1, 0, 4]):
            player_stats = statistics.get_player_statistics('A')
            self.assertEqual(player_stats['goals'], 2)
            self.assertEqual(player_stats['appearances'], 4)
        with mock.patch('services.statistics_service.get_player_statistics', return_value=None):
            self.assertIsNone(statistics.get_player_advanced_metrics('A'))
        with mock.patch('services.statistics_service.get_player_statistics', return_value={'player_id': 1, 'goals': 2, 'assists': 1, 'appearances': 2}):
            self.assertEqual(statistics.get_player_advanced_metrics('A')['goals_per_90'], 1.0)
        with mock.patch('services.statistics_service.get_player_statistics', return_value={'player_id': 1, 'goals': 0, 'assists': 0, 'appearances': 0}):
            self.assertEqual(statistics.get_player_advanced_metrics('A')['minutes_played'], 0)
        with mock.patch('services.statistics_service.clubs_repo.get_by_id', return_value={'id': 1}):
            self.assertEqual(statistics._resolve_club_id('1'), 1)
        with mock.patch('services.statistics_service.clubs_repo.get_by_id', return_value=None), \
             mock.patch('services.statistics_service.clubs_repo.get_by_name', return_value={'id': 2}):
            self.assertEqual(statistics._resolve_club_id('A'), 2)
        self.assertIsNone(statistics._resolve_club_id(None))
        with mock.patch('services.statistics_service.players_repo.get_by_id', return_value={'id': 1}):
            self.assertEqual(statistics._resolve_player_id('1'), 1)
        with mock.patch('services.statistics_service.players_repo.get_by_id', return_value=None), \
             mock.patch('services.statistics_service.players_repo.get_by_name', return_value={'id': 2}):
            self.assertEqual(statistics._resolve_player_id('A'), 2)
        self.assertIsNone(statistics._resolve_player_id(None))

        self.assertEqual(matches._resolve_club_id(None), None)
        with mock.patch('services.matches_service.clubs_repo.get_by_id', return_value={'id': 1}):
            self.assertEqual(matches._resolve_club_id('1'), 1)
        with mock.patch('services.matches_service.clubs_repo.get_by_id', return_value=None), \
             mock.patch('services.matches_service.clubs_repo.get_by_name', return_value={'id': 2}):
            self.assertEqual(matches._resolve_club_id('A'), 2)
        with mock.patch('services.matches_service._resolve_club_id', side_effect=[None, 2]):
            self.assertIn('не съществува', matches.record_match('A', 'B', '2025-01-01'))
        with mock.patch('services.matches_service._resolve_club_id', side_effect=[1, 1]):
            self.assertIn('едни и същи', matches.record_match('A', 'A', '2025-01-01'))
        with mock.patch('services.matches_service._resolve_club_id', side_effect=[1, 2]), \
             mock.patch('services.matches_service.leagues_repo.resolve_id', return_value=None):
            self.assertIn('не съществува', matches.record_match('A', 'B', '2025-01-01', league_id='X'))
        with mock.patch('services.matches_service._resolve_club_id', side_effect=[1, 2]):
            self.assertIn('цяло число', matches.record_match('A', 'B', '2025-01-01', round_no='bad'))
        with mock.patch('services.matches_service._resolve_club_id', side_effect=[1, 2]), \
             mock.patch('services.matches_service.matches_repo.create', return_value=None):
            self.assertIn('Грешка', matches.record_match('A', 'B', '2025-01-01'))
        with mock.patch('services.matches_service._resolve_club_id', side_effect=[1, 2]), \
             mock.patch('services.matches_service.matches_repo.create', side_effect=RuntimeError('x')):
            self.assertIn('Грешка', matches.record_match('A', 'B', '2025-01-01'))
        with mock.patch('services.matches_service._resolve_club_id', side_effect=[1, 2]), \
             mock.patch('services.matches_service.leagues_repo.resolve_id', return_value=9), \
             mock.patch('services.matches_service.matches_repo.create', return_value=3), \
             mock.patch('services.matches_service.matches_repo.set_played') as set_played:
            self.assertIn('ID 3', matches.record_match('A', 'B', '2025-01-01', 1, 0, 'League', 2))
            set_played.assert_called_once_with(3)
        self.assertIn('цяло число', matches.show_round('bad', 'league'))
        with mock.patch('services.matches_service.leagues_repo.resolve_id', return_value=None):
            self.assertIn('не съществува', matches.show_round('1', 'league'))
        with mock.patch('services.matches_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.matches_service.matches_repo.get_by_league', return_value=[]):
            self.assertIn('Няма мачове', matches.show_round('1', 'league'))
        with mock.patch('services.matches_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.matches_service.matches_repo.get_by_league', return_value=[
                 {'id': 1, 'match_date': '2025-01-01', 'home_name': 'A', 'away_name': 'B', 'home_goals': None, 'away_goals': None, 'is_played': 0},
                 {'id': 2, 'match_date': '2025-01-02', 'home_name': 'C', 'away_name': 'D', 'home_goals': 2, 'away_goals': 1, 'is_played': 1},
             ]):
            text = matches.show_round('1', 'league')
            self.assertIn('ПРЕДСТОЯЩ', text)
            self.assertIn('ИЗИГРАН', text)
        with mock.patch('services.matches_service.matches_repo.get_by_id', return_value={'id': 7}):
            self.assertEqual(matches.get_match(7), {'id': 7})
        with mock.patch('services.matches_service.matches_repo.exists', return_value=False):
            self.assertEqual(matches.get_match_events('1'), 'Мачът не е намерен.')
        with mock.patch('services.matches_service.matches_repo.exists', return_value=True), \
             mock.patch('services.matches_service.events_repo.get_by_match', return_value=[]):
            self.assertEqual(matches.get_match_events('1'), 'Няма записани събития за този мач.')
        with mock.patch('services.matches_service.matches_repo.exists', return_value=True), \
             mock.patch('services.matches_service.events_repo.get_by_match', return_value=[
                 {'minute': 10, 'player_name': 'A', 'event_type': 'goal', 'is_own_goal': 1},
                 {'minute': 20, 'player_name': 'B', 'event_type': 'yellow', 'is_own_goal': 0},
                 {'minute': 30, 'player_name': 'C', 'event_type': 'red', 'is_own_goal': 0},
                 {'minute': 40, 'player_name': 'D', 'event_type': 'assist', 'is_own_goal': 0},
                 {'minute': None, 'player_name': None, 'event_type': 'appearance', 'is_own_goal': 0},
                 {'minute': 50, 'player_name': 'F', 'event_type': 'mystery', 'is_own_goal': 0},
             ]):
            text = matches.get_match_events('1')
            self.assertIn('автогол', text)
            self.assertIn('ЖК', text)
            self.assertIn('ЧВ', text)
            self.assertIn('АСИСТЕНЦИЯ', text)
            self.assertIn('ПОЯВА', text)
            self.assertIn('mystery', text)
        with mock.patch('services.matches_service._resolve_league_id', return_value=None):
            self.assertIn('не съществува', matches.get_league_fixtures('X'))
        with mock.patch('services.matches_service._resolve_league_id', return_value=1), \
             mock.patch('services.matches_service.matches_repo.get_by_league', return_value=[]):
            self.assertIn('Няма мачове', matches.get_league_fixtures('X'))
        with mock.patch('services.matches_service._resolve_league_id', return_value=1), \
             mock.patch('services.matches_service.matches_repo.get_by_league', return_value=[{'match_date': '2025-01-01', 'home_name': 'A', 'away_name': 'B', 'home_goals': 1, 'away_goals': None}]):
            self.assertIn('1--', matches.get_league_fixtures('X'))
        with mock.patch('services.matches_service.events_repo.create', return_value=None):
            self.assertIn('Грешка', matches.record_event(1, 1, 1, 'goal'))
        with mock.patch('services.matches_service.events_repo.create', return_value=1):
            self.assertIn('успешно', matches.record_event(1, 1, 1, 'goal'))
        self.assertIsNone(matches._resolve_match_id(None))
        with mock.patch('services.matches_service.matches_repo.exists', return_value=True):
            self.assertEqual(matches._resolve_match_id('1'), 1)
        with mock.patch('services.matches_service.matches_repo.exists', return_value=False):
            self.assertIsNone(matches._resolve_match_id('bad'))
        self.assertIsNone(matches._resolve_league_id(None))
        with mock.patch('services.matches_service.leagues_repo.resolve_id', return_value=4):
            self.assertEqual(matches._resolve_league_id('X'), 4)

        self.assertEqual(leagues.create_league('', '2025'), 'Името на лигата не може да бъде празно.')
        self.assertEqual(leagues.create_league('A', ''), 'Сезонът не може да бъде празен.')
        self.assertIn('Невалиден формат', leagues.create_league('A', 'bad'))
        with mock.patch('services.leagues_service.leagues_repo.get_by_name_season', return_value={'id': 1}):
            self.assertIn('вече съществува', leagues.create_league('A', '2025'))
        with mock.patch('services.leagues_service.leagues_repo.get_by_name_season', return_value=None), \
             mock.patch('services.leagues_service.leagues_repo.create', return_value=None):
            self.assertIn('Грешка', leagues.create_league('A', '2025'))
        with mock.patch('services.leagues_service.leagues_repo.get_by_name_season', return_value=None), \
             mock.patch('services.leagues_service.leagues_repo.create', return_value=1):
            self.assertIn('създадена успешно', leagues.create_league('A', '2025'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=None):
            self.assertIn('Няма лига', leagues.add_club_to_league('L', 'C'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.clubs_repo.get_by_id', return_value=None), \
             mock.patch('services.leagues_service.clubs_repo.get_by_name', return_value=None):
            self.assertIn('не съществува', leagues.add_club_to_league('L', 'C'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.clubs_repo.get_by_name', return_value={'id': 2}), \
             mock.patch('services.leagues_service.leagues_repo.add_team', return_value=None):
            self.assertIn('Грешка', leagues.add_club_to_league('L', 'C'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.clubs_repo.get_by_name', return_value={'id': 2}), \
             mock.patch('services.leagues_service.leagues_repo.add_team', return_value=1):
            self.assertIn('успешно', leagues.add_club_to_league('L', 'C'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.clubs_repo.get_by_id', return_value={'id': 2}), \
             mock.patch('services.leagues_service.leagues_repo.add_team', return_value=1):
            self.assertIn('успешно', leagues.add_club_to_league('L', '2'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=None):
            self.assertEqual(leagues.get_league_teams('L'), [])
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.leagues_repo.get_teams', return_value=None):
            self.assertEqual(leagues.get_league_teams('L'), [])
        with mock.patch('services.leagues_service.get_league_teams', return_value=[]):
            self.assertIn('Недостатъчно', leagues.generate_round_robin('L'))
        with mock.patch('services.leagues_service.get_league_teams', return_value=[{'id': 1}, {'id': 2}]), \
             mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=None):
            self.assertIn('Няма лига', leagues.generate_round_robin('L'))
        with mock.patch('services.leagues_service.get_league_teams', return_value=[{'id': 1}, {'id': 2}]), \
             mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.matches_repo.get_by_league', return_value=[{'id': 1}]):
            self.assertIn('вече е генерирана', leagues.generate_round_robin('L'))
        with mock.patch('services.leagues_service.get_league_teams', return_value=[{'id': 1}, {'id': 2}, {'id': 3}]), \
             mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.matches_repo.get_by_league', return_value=[]), \
             mock.patch('services.leagues_service.matches_repo.create', return_value=1):
            self.assertIn('Създадени', leagues.generate_round_robin('L', start_date='bad'))
            self.assertIn('Създадени', leagues.generate_round_robin('L', double_round=True, start_date='2025-01-01'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=None):
            self.assertIn('Няма лига', leagues.get_standings('L'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.leagues_repo.get_by_id', return_value=None):
            self.assertIn('Няма лига с ID', leagues.get_standings('L'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.leagues_repo.get_by_id', return_value={'name': 'A', 'season': '2025'}), \
             mock.patch('services.standings_service.calculate_standings', return_value=[]):
            self.assertIn('Няма отбори', leagues.get_standings('L'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.leagues_repo.get_by_id', return_value={'name': 'A', 'season': '2025'}), \
             mock.patch('services.standings_service.calculate_standings', return_value=[{'position': 1, 'team': 'A', 'mp': 1, 'w': 1, 'd': 0, 'l': 0, 'gf': 2, 'ga': 1, 'gd': 1, 'pts': 3}]):
            self.assertIn('1. A', leagues.get_standings('L'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=None):
            self.assertEqual(leagues.remove_club_from_league('L', 'C'), 'Лигата не съществува.')
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.clubs_repo.get_by_name', return_value=None), \
             mock.patch('services.leagues_service.clubs_repo.get_by_id', return_value=None):
            self.assertEqual(leagues.remove_club_from_league('L', 'C'), 'Клубът не съществува.')
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.clubs_repo.get_by_name', return_value={'id': 2}), \
             mock.patch('services.leagues_service.leagues_repo.get_teams', return_value=[]):
            self.assertEqual(leagues.remove_club_from_league('L', 'C'), 'Клубът не е в тази лига.')
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.clubs_repo.get_by_name', return_value={'id': 2}), \
             mock.patch('services.leagues_service.leagues_repo.get_teams', return_value=[{'id': 2}]), \
             mock.patch('services.leagues_service.matches_repo.get_by_league', return_value=[{'id': 1}]):
            self.assertIn('Не можете да премахнете', leagues.remove_club_from_league('L', 'C'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.clubs_repo.get_by_name', return_value={'id': 2}), \
             mock.patch('services.leagues_service.leagues_repo.get_teams', return_value=[{'id': 2}]), \
             mock.patch('services.leagues_service.matches_repo.get_by_league', return_value=[]), \
             mock.patch('services.leagues_service.leagues_repo.remove_team', return_value=None):
            self.assertIn('Грешка', leagues.remove_club_from_league('L', 'C'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.clubs_repo.get_by_name', return_value={'id': 2}), \
             mock.patch('services.leagues_service.leagues_repo.get_teams', return_value=[{'id': 2}]), \
             mock.patch('services.leagues_service.matches_repo.get_by_league', return_value=[]), \
             mock.patch('services.leagues_service.leagues_repo.remove_team', return_value=1):
            self.assertIn('успешно', leagues.remove_club_from_league('L', 'C'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.clubs_repo.get_by_id', return_value={'id': 2}), \
             mock.patch('services.leagues_service.leagues_repo.get_teams', return_value=[{'id': 2}]), \
             mock.patch('services.leagues_service.matches_repo.get_by_league', return_value=[]), \
             mock.patch('services.leagues_service.leagues_repo.remove_team', return_value=1):
            self.assertIn('успешно', leagues.remove_club_from_league('L', '2'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=None):
            self.assertIn('Няма лига', leagues.get_fixtures('L'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.matches_repo.get_by_league', return_value=[]):
            self.assertIn('Няма насрочени', leagues.get_fixtures('L'))
        with mock.patch('services.leagues_service.leagues_repo.resolve_id', return_value=1), \
             mock.patch('services.leagues_service.matches_repo.get_by_league', return_value=[{'match_date': '2025-01-01', 'home_name': 'A', 'away_name': 'B', 'home_goals': 1, 'away_goals': 0}]):
            self.assertIn('A vs B', leagues.get_fixtures('L'))

        with mock.patch('services.transfers_service.players_repo.get_by_id', return_value=None), \
             mock.patch('services.transfers_service.players_repo.get_by_name', return_value=None):
            self.assertIn('не съществува', transfers.transfer_player('P', 'C'))
        self.assertEqual(transfers._validate_transfer_date(None)[1], None)
        self.assertIn('Невалидна дата', transfers._validate_transfer_date('bad')[1])
        self.assertEqual(transfers._validate_fee('')[1], None)
        self.assertIn('не може да бъде отрицателна', transfers._validate_fee('-1')[1])
        self.assertIn('Невалидна сума', transfers._validate_fee('bad')[1])
        self.assertTrue(transfers._is_free_agent(None))
        self.assertFalse(transfers._is_free_agent('club'))
        with mock.patch('services.transfers_service._resolve_player', return_value=1), \
             mock.patch('services.transfers_service._resolve_club', return_value=None):
            self.assertIn('не съществува', transfers.transfer_player('P', 'C'))
        with mock.patch('services.transfers_service._resolve_player', return_value=1), \
             mock.patch('services.transfers_service._resolve_club', return_value=2), \
             mock.patch('services.transfers_service.players_repo.get_club_and_number', return_value=None):
            self.assertIn('не съществува', transfers.transfer_player('P', 'C'))
        with mock.patch('services.transfers_service._resolve_player', return_value=1), \
             mock.patch('services.transfers_service._resolve_club', return_value=2), \
             mock.patch('services.transfers_service.players_repo.get_club_and_number', return_value={'club_id': 2, 'number': 9, 'full_name': 'Player'}):
            self.assertIn('вече е в този клуб', transfers.transfer_player('P', 'C'))
        with mock.patch('services.transfers_service._resolve_player', return_value=1), \
             mock.patch('services.transfers_service._resolve_club', side_effect=[2, None]), \
             mock.patch('services.transfers_service.players_repo.get_club_and_number', return_value={'club_id': 1, 'number': 9, 'full_name': 'Player'}):
            self.assertIn('не съществува', transfers.transfer_player('P', 'C', from_club_identifier='X'))
        with mock.patch('services.transfers_service._resolve_player', return_value=1), \
             mock.patch('services.transfers_service._resolve_club', return_value=2), \
             mock.patch('services.transfers_service.players_repo.get_club_and_number', return_value={'club_id': None, 'number': 9, 'full_name': 'Player'}):
            self.assertIn('свободен агент', transfers.transfer_player('P', 'C', from_club_identifier='Club'))
        with mock.patch('services.transfers_service._resolve_player', return_value=1), \
             mock.patch('services.transfers_service._resolve_club', return_value=2), \
             mock.patch('services.transfers_service.players_repo.get_club_and_number', return_value={'club_id': 1, 'number': 9, 'full_name': 'Player'}):
            self.assertIn('не е свободен агент', transfers.transfer_player('P', 'C'))
        with mock.patch('services.transfers_service._resolve_player', return_value=1), \
             mock.patch('services.transfers_service._resolve_club', side_effect=[2, 3]), \
             mock.patch('services.transfers_service.players_repo.get_club_and_number', return_value={'club_id': 1, 'number': 9, 'full_name': 'Player'}):
            self.assertIn('не играе в посочения клуб', transfers.transfer_player('P', 'C', from_club_identifier='3'))
        with mock.patch('services.transfers_service._resolve_player', return_value=1), \
             mock.patch('services.transfers_service._resolve_club', side_effect=[2, 1]), \
             mock.patch('services.transfers_service.players_repo.get_club_and_number', return_value={'club_id': 1, 'number': 9, 'full_name': 'Player'}), \
             mock.patch('services.transfers_service.players_repo.check_number_conflict', return_value={'id': 99}), \
             mock.patch('services.transfers_service.players_repo.get_used_numbers', return_value={1, 2, 9}), \
             mock.patch('services.transfers_service.connect', return_value=None):
            self.assertIn('Грешка при свързване', transfers.transfer_player('P', 'C', from_club_identifier='1'))
        conn = mock.Mock()
        with mock.patch('services.transfers_service._resolve_player', return_value=1), \
             mock.patch('services.transfers_service._resolve_club', side_effect=[2, 1]), \
             mock.patch('services.transfers_service.players_repo.get_club_and_number', return_value={'club_id': 1, 'number': 9, 'full_name': 'Player'}), \
             mock.patch('services.transfers_service.players_repo.check_number_conflict', return_value={'id': 99}), \
             mock.patch('services.transfers_service.players_repo.get_used_numbers', return_value={1, 2, 9}), \
             mock.patch('services.transfers_service.connect', return_value=conn), \
             mock.patch('services.transfers_service.players_repo.update_club_and_number'), \
             mock.patch('services.transfers_service.transfers_repo.create'), \
             mock.patch('services.transfers_service.commit'), \
             mock.patch('services.transfers_service.log_command'):
            self.assertIn('Присвоен нов номер', transfers.transfer_player('P', 'C', from_club_identifier='1'))
        with mock.patch('services.transfers_service._resolve_player', return_value=1), \
             mock.patch('services.transfers_service._resolve_club', side_effect=[2, 1]), \
             mock.patch('services.transfers_service.players_repo.get_club_and_number', return_value={'club_id': 1, 'number': 9, 'full_name': 'Player'}), \
             mock.patch('services.transfers_service.players_repo.check_number_conflict', return_value=None), \
             mock.patch('services.transfers_service.connect', return_value=conn), \
             mock.patch('services.transfers_service.players_repo.update_club_and_number', side_effect=RuntimeError('boom')), \
             mock.patch('services.transfers_service.rollback'), \
             mock.patch('services.transfers_service.log_command'):
            self.assertIn('Грешка при трансфер', transfers.transfer_player('P', 'C', from_club_identifier='1'))
        with mock.patch('services.transfers_service.players_repo.get_by_id', return_value={'id': 1}):
            self.assertEqual(transfers._resolve_player('1'), 1)
        with mock.patch('services.transfers_service.players_repo.get_by_id', return_value=None), \
             mock.patch('services.transfers_service.players_repo.get_by_name', return_value={'id': 2}):
            self.assertEqual(transfers._resolve_player('A'), 2)
        self.assertIsNone(transfers._resolve_club(None))
        with mock.patch('services.transfers_service.clubs_repo.get_by_id', return_value={'id': 1}):
            self.assertEqual(transfers._resolve_club('1'), 1)
        with mock.patch('services.transfers_service.clubs_repo.get_by_id', return_value=None), \
             mock.patch('services.transfers_service.clubs_repo.get_by_name', return_value={'id': 2}):
            self.assertEqual(transfers._resolve_club('A'), 2)
        with mock.patch('services.transfers_service._resolve_player', return_value=None):
            self.assertIn('не съществува', transfers.list_transfers_by_player('P'))
        with mock.patch('services.transfers_service._resolve_player', return_value=1), \
             mock.patch('services.transfers_service.transfers_repo.get_by_player', return_value=[]):
            self.assertIn('Няма трансфери', transfers.list_transfers_by_player('P'))
        with mock.patch('services.transfers_service._resolve_player', return_value=1), \
             mock.patch('services.transfers_service.transfers_repo.get_by_player', return_value=[{'player_name': 'P', 'from_club_name': None, 'to_club_name': 'Club', 'fee': 1.5, 'transfer_date': '2025-01-01'}]):
            self.assertIn('свободен агент', transfers.list_transfers_by_player('P'))
        with mock.patch('services.transfers_service._resolve_club', return_value=None):
            self.assertIn('не съществува', transfers.list_transfers_by_club('C'))
        with mock.patch('services.transfers_service._resolve_club', return_value=1), \
             mock.patch('services.transfers_service.transfers_repo.get_by_club', return_value=[]):
            self.assertIn('Няма трансфери', transfers.list_transfers_by_club('C'))
        with mock.patch('services.transfers_service._resolve_club', return_value=1), \
             mock.patch('services.transfers_service.transfers_repo.get_by_club', return_value=[
                 {'from_club_name': None, 'to_club_name': 'To', 'player_name': 'P', 'fee': 1.0, 'transfer_date': '2025-01-01', 'from_club_id': 1},
                 {'from_club_name': 'From', 'to_club_name': 'To', 'player_name': 'Q', 'fee': None, 'transfer_date': '2025-01-02', 'from_club_id': 2},
             ]):
            text = transfers.list_transfers_by_club('C')
            self.assertIn('напуска', text)
            self.assertIn('пристига', text)

        with mock.patch('services.standings_service.standings_repo.get_league_by_id', return_value=None), \
             mock.patch('services.standings_service.standings_repo.get_league_by_name', return_value=None), \
             mock.patch('services.standings_service.standings_repo.get_league_by_name_and_season', return_value=None):
            self.assertEqual(standings.calculate_standings('L'), [])
        with mock.patch('services.standings_service.standings_repo.get_league_by_id', return_value={'id': 1}), \
             mock.patch('services.standings_service.standings_repo.get_league_teams', return_value=[]):
            self.assertEqual(standings.calculate_standings('1'), [])
        with mock.patch('services.standings_service.standings_repo.get_league_by_name_and_season', return_value={'id': 1}), \
             mock.patch('services.standings_service.standings_repo.get_league_teams', return_value=[]):
            self.assertEqual(standings.calculate_standings('League', '2025'), [])
        teams = [{'id': 1, 'name': 'A'}, {'id': 2, 'name': 'B'}]
        matches_list = [
            {'id': 1, 'home_team_id': 1, 'away_team_id': 2, 'home_goals': 2, 'away_goals': 1},
            {'id': 2, 'home_team_id': 2, 'away_team_id': 1, 'home_goals': 1, 'away_goals': 1},
            {'id': 3, 'home_team_id': 3, 'away_team_id': 1, 'home_goals': 0, 'away_goals': 0},
        ]
        with mock.patch('services.standings_service.standings_repo.get_league_by_name', return_value={'id': 1}), \
             mock.patch('services.standings_service.standings_repo.get_league_teams', return_value=teams), \
             mock.patch('services.standings_service.standings_repo.validate_match_consistency', return_value=[{'id': 99}]), \
             mock.patch('services.standings_service.standings_repo.get_played_matches', return_value=matches_list), \
             mock.patch('services.standings_service.standings_repo.get_matches_with_scores_not_played', return_value=[]), \
             mock.patch('services.standings_service.log_command') as log_command:
            table = standings.calculate_standings('League')
            self.assertEqual(table[0]['position'], 1)
            self.assertTrue(log_command.called)
        standings.AUTO_MARK_PLAYED = False
        with mock.patch('services.standings_service.standings_repo.get_league_by_name', return_value={'id': 1}), \
             mock.patch('services.standings_service.standings_repo.get_league_teams', return_value=teams), \
             mock.patch('services.standings_service.standings_repo.validate_match_consistency', return_value=[]), \
             mock.patch('services.standings_service.standings_repo.get_played_matches', return_value=[]):
            self.assertEqual(len(standings.calculate_standings('League')), 2)
        standings.AUTO_MARK_PLAYED = True
        tied = [
            {'team_id': 1, 'team': 'A', 'pts': 1, 'gd': 0, 'gf': 1},
            {'team_id': 2, 'team': 'B', 'pts': 1, 'gd': 0, 'gf': 1},
        ]
        standings._apply_head_to_head(tied, [{'home_team_id': 1, 'away_team_id': 2, 'home_goals': 2, 'away_goals': 1}], {1: 'A', 2: 'B'})
        self.assertEqual(tied[0]['team_id'], 1)
        standings._apply_head_to_head([{'team_id': 1, 'team': 'A', 'pts': 3, 'gd': 1, 'gf': 2}], [], {1: 'A'})

        self.assertEqual(h_ai.handle_predict_match({}), 'Формат: Prediction [отбор1] vs [отбор2]')
        with mock.patch('handlers.handler_ai.ai_service.predict_match', side_effect=ValueError('bad')):
            self.assertEqual(h_ai.handle_predict_match({'team1': 'A', 'team2': 'B'}), 'bad')
        with mock.patch('handlers.handler_ai.ai_service.predict_match', return_value={'home': 1, 'draw': 2, 'away': 97}):
            self.assertIn('🏠 A Win', h_ai.handle_predict_match({'team1': 'A', 'team2': 'B'}))
        self.assertIn('Формат', h_matches.handle_show_round({'round_no': None, 'league_name': None}))
        with mock.patch('handlers.handler_matches.matches.show_round', return_value='ok'):
            self.assertEqual(h_matches.handle_show_round({'round_no': '1', 'league_name': 'L'}), 'ok')
        self.assertIn('Формат', h_matches.handle_show_events({}))
        with mock.patch('handlers.handler_matches.matches.get_match_events', return_value='events'):
            self.assertEqual(h_matches.handle_show_events({'match_id': '1'}), 'events')
        self.assertIn('Формат', h_standings.handle_show_standings({}))
        with mock.patch('handlers.handler_standings.standings.calculate_standings', return_value=[]):
            self.assertIn('Няма намерена лига', h_standings.handle_show_standings({'league_identifier': 'L'}))
        with mock.patch('handlers.handler_standings.standings.calculate_standings', return_value=[{'position': 1, 'team': 'A', 'mp': 0, 'w': 0, 'd': 0, 'l': 0, 'gf': 0, 'ga': 0, 'gd': 0, 'pts': 0}]):
            self.assertIn('Няма изиграни мачове.', h_standings.handle_show_standings({'league_identifier': 'L'}))
