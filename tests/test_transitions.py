import unittest
from transitions import Machine

class TestTransitions(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_transitions_package(self):
		states = ['A', 'B', 'C']  # 状態の定義

		class Model(object):
			pass

		model = Model()
		machine = Machine(model=model, states=states, initial=states[0],
                          ordered_transitions=True, auto_transitions=False)

		self.assertEqual(model.state, states[0])
		self.assertTrue(model.next_state())
		self.assertEqual(model.state, states[1])
		self.assertTrue(model.next_state())
		self.assertEqual(model.state, states[2])
		self.assertTrue(model.next_state())

if __name__ == '__main__':
	unittest.main()