import importlib
from unittest import mock

from test_support import BasePatchedTestCase


class TestValidators(BasePatchedTestCase):
    def test_validator_branches(self):
        validators = importlib.import_module('validators')
        self.assertEqual(validators.validate_minute(None), (False, 'Минутата е задължителна.'))
        self.assertIn('цяло число', validators.validate_minute('bad')[1])
        self.assertIn('между 1 и 120', validators.validate_minute('0')[1])
        self.assertEqual(validators.validate_minute('10'), (True, ''))
        self.assertIn('Резултатът е задължителен', validators.validate_score(None, 1)[1])
        self.assertIn('две цели числа', validators.validate_score('a', 1)[1])
        self.assertIn('отрицателни', validators.validate_score('-1', 1)[1])
        self.assertEqual(validators.validate_score('1', '2'), (True, ''))
        with mock.patch('validators.matches_repo.get_by_id', return_value=None):
            self.assertIn('Мачът не съществува', validators.validate_player_in_match(1, 1)[1])
        with mock.patch('validators.matches_repo.get_by_id', return_value={'home_team_id': 1, 'away_team_id': 2}), \
             mock.patch('validators.players_repo.get_club_id', return_value=None):
            self.assertIn('Играчът не съществува', validators.validate_player_in_match(1, 1)[1])
        with mock.patch('validators.matches_repo.get_by_id', return_value={'home_team_id': 1, 'away_team_id': 2}), \
             mock.patch('validators.players_repo.get_club_id', return_value=3):
            self.assertIn('не участва', validators.validate_player_in_match(1, 1)[1])
        with mock.patch('validators.matches_repo.get_by_id', return_value={'home_team_id': 1, 'away_team_id': 2}), \
             mock.patch('validators.players_repo.get_club_id', return_value=1):
            self.assertEqual(validators.validate_player_in_match(1, 1), (True, ''))
        with mock.patch('validators.matches_repo.is_played', return_value=True):
            self.assertIn('вече има записан', validators.validate_no_duplicate_result(1)[1])
        with mock.patch('validators.matches_repo.is_played', return_value=False):
            self.assertEqual(validators.validate_no_duplicate_result(1), (True, ''))
        with mock.patch('validators.events_repo.has_red_in_match', return_value=True):
            self.assertIn('червен картон', validators.validate_no_goal_after_red(1, 1)[1])
        with mock.patch('validators.events_repo.has_red_in_match', return_value=False):
            self.assertEqual(validators.validate_no_goal_after_red(1, 1), (True, ''))
        with mock.patch('validators.events_repo.count_cards_in_match', return_value={'red': 1, 'yellow': 0}):
            self.assertIn('вече е получил червен', validators.validate_card_allowed(1, 1, 'Y')[1])
        with mock.patch('validators.events_repo.count_cards_in_match', return_value={'red': 0, 'yellow': 1}):
            self.assertIn('Втори жълт', validators.validate_card_allowed(1, 1, 'Y')[1])
            self.assertEqual(validators.validate_card_allowed(1, 1, 'R'), (True, ''))
        with mock.patch('validators.events_repo.count_cards_in_match', return_value={'red': 0, 'yellow': 0}):
            self.assertEqual(validators.validate_card_allowed(1, 1, 'Y'), (True, ''))
        self.assertIn('задължителна', validators.validate_transfer_date('')[1])
        self.assertIn('Невалидна дата', validators.validate_transfer_date('bad')[1])
        self.assertEqual(validators.validate_transfer_date('2025-01-01'), (True, ''))
        self.assertEqual(validators.validate_transfer_fee(''), (True, ''))
        self.assertIn('не може да бъде отрицателна', validators.validate_transfer_fee('-1')[1])
        self.assertIn('Невалидна сума', validators.validate_transfer_fee('bad')[1])
        self.assertEqual(validators.validate_transfer_fee('1.5'), (True, ''))
        self.assertIn('свободен агент', validators.validate_from_club(None, 'club')[1])
        self.assertEqual(validators.validate_from_club(None, 'няма'), (True, ''))
        self.assertIn('не е свободен агент', validators.validate_from_club(1, 'няма')[1])
        with mock.patch('validators.clubs_repo.get_by_name', return_value=None):
            self.assertIn('Клубът не съществува', validators.validate_from_club(1, 'club')[1])
        with mock.patch('validators.clubs_repo.get_by_name', return_value={'id': 2}):
            self.assertIn('не играе в посочения клуб', validators.validate_from_club(1, 'club')[1])
        with mock.patch('validators.clubs_repo.get_by_name', return_value={'id': 1}):
            self.assertEqual(validators.validate_from_club(1, 'club'), (True, ''))
        with mock.patch('validators.clubs_repo.get_by_name', return_value=None):
            self.assertIn('Клубът не съществува', validators.validate_player_belongs_to_club(1, 'club')[1])
        with mock.patch('validators.clubs_repo.get_by_name', return_value={'id': 1}), \
             mock.patch('validators.players_repo.get_club_id', return_value=None):
            self.assertIn('Играчът не съществува', validators.validate_player_belongs_to_club(1, 'club')[1])
        with mock.patch('validators.clubs_repo.get_by_name', return_value={'id': 1}), \
             mock.patch('validators.players_repo.get_club_id', return_value=2):
            self.assertIn('не принадлежи', validators.validate_player_belongs_to_club(1, 'club')[1])
        with mock.patch('validators.clubs_repo.get_by_name', return_value={'id': 1}), \
             mock.patch('validators.players_repo.get_club_id', return_value=1):
            self.assertEqual(validators.validate_player_belongs_to_club(1, 'club'), (True, ''))
