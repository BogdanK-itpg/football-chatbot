import importlib
from unittest import mock

from test_support import BasePatchedTestCase


class TestRepositoryModules(BasePatchedTestCase):
    def test_repo_helpers_and_query_composition(self):
        clubs_repo = importlib.import_module('repositories.clubs_repo')
        players_repo = importlib.import_module('repositories.players_repo')
        leagues_repo = importlib.import_module('repositories.leagues_repo')
        matches_repo = importlib.import_module('repositories.matches_repo')
        events_repo = importlib.import_module('repositories.events_repo')
        transfers_repo = importlib.import_module('repositories.transfers_repo')
        standings_repo = importlib.import_module('repositories.standings_repo')

        with mock.patch('repositories.clubs_repo.fetch_one', return_value={'id': 1}) as fetch_one, \
             mock.patch('repositories.clubs_repo.fetch_all', return_value=[{'id': 2, 'name': 'Левски София'}]):
            self.assertEqual(clubs_repo.get_by_name('levski'), {'id': 1})
            fetch_one.return_value = None
            self.assertEqual(clubs_repo.get_by_name('Левски'), {'id': 2, 'name': 'Левски София'})
            self.assertIsNone(clubs_repo.get_by_name('Несъществуващ'))

        with mock.patch('repositories.clubs_repo.execute', return_value=1):
            self.assertEqual(clubs_repo.create(' Test '), 1)
            self.assertIsNone(clubs_repo.update(1))
            self.assertEqual(clubs_repo.update(1, name='X'), 1)
            self.assertEqual(clubs_repo.delete(1), 1)
        with mock.patch('repositories.clubs_repo.fetch_one', return_value={'x': 1}):
            self.assertTrue(clubs_repo.exists(1))
        with mock.patch('repositories.clubs_repo.fetch_one', return_value=None):
            self.assertFalse(clubs_repo.exists(1))

        with mock.patch('repositories.players_repo.fetch_one', return_value={'id': 1}) as fetch_one, \
             mock.patch('repositories.players_repo.fetch_all', return_value=[{'id': 3, 'full_name': 'Иван Иванов', 'club_id': 1}]):
            self.assertEqual(players_repo.get_by_name('ivan'), {'id': 1})
            fetch_one.return_value = None
            self.assertEqual(players_repo.get_by_name('Иван'), {'id': 3, 'full_name': 'Иван Иванов', 'club_id': 1})
            self.assertIsNone(players_repo.get_by_name('No'))
        with mock.patch('repositories.players_repo.execute', return_value=2):
            self.assertEqual(players_repo.create(1, 'A', '2000-01-01', 'BG', 'GK', 1, 'Активен'), 2)
            self.assertIsNone(players_repo.update(1))
            self.assertEqual(players_repo.update(1, status='X'), 2)
            self.assertEqual(players_repo.delete(1), 2)
            self.assertEqual(players_repo.update_club_and_number(1, 2, 3, conn=mock.Mock()), 2)
        with mock.patch('repositories.players_repo.fetch_one', return_value={'club_id': 7}):
            self.assertEqual(players_repo.get_club_id(1), 7)
        with mock.patch('repositories.players_repo.fetch_one', return_value=None):
            self.assertIsNone(players_repo.get_club_id(1))
        with mock.patch('repositories.players_repo.fetch_one', return_value={'x': 1}):
            self.assertTrue(players_repo.exists(1))
            self.assertTrue(players_repo.exists_by_name_club('A', 1))
            self.assertEqual(players_repo.get_club_and_number(1), {'x': 1})
            self.assertEqual(players_repo.check_number_conflict(1, 9, 2), {'x': 1})
        with mock.patch('repositories.players_repo.fetch_one', return_value=None):
            self.assertFalse(players_repo.exists(1))
            self.assertFalse(players_repo.exists_by_name_club('A', 1))
        with mock.patch('repositories.players_repo.fetch_all', return_value=[{'number': 1}, {'number': 7}]):
            self.assertEqual(players_repo.get_used_numbers(1), {1, 7})

        with mock.patch('repositories.leagues_repo.fetch_one', side_effect=[{'id': 1}, {'id': 2}, None]):
            self.assertEqual(leagues_repo.resolve_id('1'), 1)
            self.assertEqual(leagues_repo.resolve_id('Първа Лига'), 2)
            self.assertIsNone(leagues_repo.resolve_id(None))
        with mock.patch('repositories.leagues_repo.execute', return_value=5):
            self.assertEqual(leagues_repo.create('A', '2025'), 5)
            self.assertEqual(leagues_repo.add_team(1, 1), 5)
            self.assertEqual(leagues_repo.remove_team(1, 1), 5)

        self.assertIsNone(matches_repo.create(1, 1, '2025-01-01'))
        with mock.patch('repositories.matches_repo.execute', return_value=4):
            self.assertEqual(matches_repo.create(1, 2, '2025-01-01'), 4)
            self.assertEqual(matches_repo.set_score(1, 1, 0), 4)
            self.assertEqual(matches_repo.set_played(1), 4)
            self.assertEqual(matches_repo.increment_score(1, True), 4)
            self.assertEqual(matches_repo.increment_score(1, False), 4)
        with mock.patch('repositories.matches_repo.fetch_one', return_value={'x': 1}):
            self.assertTrue(matches_repo.exists(1))
        with mock.patch('repositories.matches_repo.fetch_one', return_value={'is_played': 1}):
            self.assertTrue(matches_repo.is_played(1))
        with mock.patch('repositories.matches_repo.fetch_one', return_value=None):
            self.assertFalse(matches_repo.exists(1))
            self.assertFalse(matches_repo.is_played(1))

        with mock.patch('repositories.events_repo.execute', return_value=7):
            self.assertEqual(events_repo.create(1, 1, 1, 'goal'), 7)
        with mock.patch('repositories.events_repo.fetch_one', return_value={'cnt': 2}):
            self.assertEqual(events_repo.count_by_type(1, 1, 'goal'), 2)
            self.assertEqual(events_repo.count_by_player(1, 'goal'), 2)
            self.assertTrue(events_repo.has_red_in_match(1, 1))
            self.assertEqual(events_repo.get_last_event_before_minute(1, 1, 10), {'cnt': 2})
        with mock.patch('repositories.events_repo.fetch_one', side_effect=[{'cnt': 1}, {'cnt': 0}]):
            self.assertEqual(events_repo.count_cards_in_match(1, 1), {'yellow': 1, 'red': 0})

        with mock.patch('repositories.transfers_repo.execute', return_value=9):
            self.assertEqual(transfers_repo.create(1, 1, 2, '2025-01-01'), 9)
        with mock.patch('repositories.transfers_repo.fetch_all', return_value=[{'id': 1}]), \
             mock.patch('repositories.transfers_repo.fetch_one', return_value={'id': 2}):
            self.assertEqual(transfers_repo.get_by_id(1), {'id': 2})
            self.assertEqual(transfers_repo.get_by_player(1), [{'id': 1}])
            self.assertEqual(transfers_repo.get_by_club(1), [{'id': 1}])
            self.assertEqual(transfers_repo.get_all(), [{'id': 1}])

        with mock.patch('repositories.standings_repo.fetch_one', return_value={'id': 1}), \
             mock.patch('repositories.standings_repo.fetch_all', return_value=[{'id': 2}]):
            self.assertEqual(standings_repo.get_league_by_name_and_season('A', '2025'), {'id': 1})
            self.assertEqual(standings_repo.get_league_by_name('A'), {'id': 1})
            self.assertEqual(standings_repo.get_league_by_id(1), {'id': 1})
            self.assertEqual(standings_repo.get_league_teams(1), [{'id': 2}])
            self.assertEqual(standings_repo.get_played_matches(1), [{'id': 2}])
            self.assertEqual(standings_repo.get_matches_with_scores_not_played(1), [{'id': 2}])
            self.assertEqual(standings_repo.validate_match_consistency(1), [{'id': 2}])
        with mock.patch('repositories.standings_repo.fetch_all', return_value=[]):
            self.assertEqual(standings_repo.validate_match_consistency(1), [])
