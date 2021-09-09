from unittest import TestCase

from domino import Domino


class TestBoard(TestCase):
    def test_play_domino(self):
        self.fail()


class TestDomino(TestCase):
    # def __init__(self):
    #     super().__init__()

    def test_get_id(self):
        # domino =
        self.fail()

    def test_id_to_nums(self):
        self.assertEqual(Domino.id_to_nums(0, 100), (0, 0))
        self.assertEqual(Domino.id_to_nums(16, 6), (2, 5))
        self.assertEqual(Domino.id_to_nums(40, 10), (4, 6))
        self.assertEqual(Domino.id_to_nums(65, 10), (10, 10))
        self.assertEqual(Domino.id_to_nums(0, 0), (0, 0))
        self.assertRaises(AssertionError, Domino.id_to_nums, *(66, 10))
        self.assertRaises(AssertionError, Domino.id_to_nums, *(1, 0))

    def test_check_match(self):
        domino_1 = Domino(0, 1, 6)
        domino_2 = Domino(1, 2, 6)
        domino_3 = Domino(1, 3, 6)
        domino_4 = Domino(2, 3, 6)
        self.assertEqual(domino_1.check_match(None), None)
        self.assertEqual(domino_1.check_match(3), None)
        self.assertEqual(domino_1.check_match(domino_4), None)
        self.assertEqual(domino_1.check_match(domino_2), (1, 1))
        self.assertEqual(domino_1.check_match(domino_3), (1, 1))
        self.assertEqual(domino_2.check_match(domino_4), (1, 1))
        self.assertEqual(domino_3.check_match(domino_4), (1, -1))
        self.assertEqual(domino_2.check_match(domino_3), (-1, 1))
        self.assertEqual(domino_2.check_match(domino_3), (-1, 1))

    def test_is_double(self):
        self.fail()


class TestReversibleDomino(TestCase):
    def test_get_out_facing_number(self):
        self.fail()

    def test_get_in_facing_number(self):
        self.fail()

    def test_get_out_facing_sum(self):
        self.fail()
