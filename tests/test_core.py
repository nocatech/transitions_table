import unittest, warnings, logging
from .utils import TestObject
import pandas as pd

class TestCore(unittest.TestCase):
    def setUp(self):
        self.__states = ['A', 'B', 'C', 'D', 'E']
        self.__init = self.__states[0]
        pass

    def tearDown(self):
        pass

    def test_auto_transitions(self):
        h = TestObject(states=self.__states, initial=self.__init, auto_transitions=True)
        self.helper_exc(h.table, h.staff)

    def test_ordered_transitions(self):
        h = TestObject(states=self.__states, initial=self.__init, ordered_transitions=True)
        self.helper_exc(h.table, h.staff)

    def test_all_undefined_transitions(self):
        h = TestObject(states=self.__states, initial=self.__init, auto_transitions=True, ordered_transitions=True)
        self.helper_exc(h.table, h.staff)

    def test_simple_transitions(self):
        state = ['A', 'B']
        transitions = [
            {'trigger': 'fromAtoB', 'source': 'A', 'dest': 'B'},
            {'trigger': 'fromBtoA', 'source': 'B', 'dest': 'A'},
        ]
        h = TestObject(states=state, initial=state[0], transitions=transitions)
        self.helper_exc(h.table, h.staff)

    def test_to_init_transitions(self):
        others_init_states = [state for state in self.__states if state != self.__init]
        transitions = [
            {'trigger': 'to_init',  'source':  source,   'dest': self.__init} for source in others_init_states
        ]
        h = TestObject(states=self.__states, initial=self.__init, transitions=transitions)
        self.helper_exc(h.table, h.staff)

    def test_multi_transitions(self):
        others_init_states = [state for state in self.__states if state != self.__init]
        transitions = [
            {'trigger': 'to_init',  'source': others_init_states,   'dest': self.__init},
            {'trigger': 'to_next',  'source': '*',                  'dest': others_init_states[0]},
        ]
        h = TestObject(states=self.__states, initial=self.__init, transitions=transitions)
        self.helper_exc(h.table, h.staff)

    def test_self_transitions(self):
        transitions = [
            {'trigger': 'to_self',    'source': '*', 'dest': '='},
        ]
        h = TestObject(states=self.__states, initial=self.__init, transitions=transitions)
        self.helper_exc(h.table, h.staff)

    def test_internal_transitions(self):
        transitions = [
            {'trigger': 'internal',    'source': '*', 'dest': None},
        ]
        h = TestObject(states=self.__states, initial=self.__init, transitions=transitions)
        self.helper_exc(h.table, h.staff)

    def test_replace_nan_transitions(self):
        state = ['A', 'B', 'C']
        transitions = [
            {'trigger': 'fromAtoB', 'source': 'A', 'dest': 'B'},
            {'trigger': 'fromBtoC', 'source': 'B', 'dest': 'C'},
            {'trigger': 'fromCtoA', 'source': 'C', 'dest': 'A'},
        ]
        h = TestObject(states=state, initial=state[0], transitions=transitions, undefined_id='xxx')
        self.helper_exc(h.table, h.staff)

    def test_replace_internal_transitions(self):
        state = ['A', 'B']
        transitions = [
            {'trigger': 'internal', 'source': 'A', 'dest': None},
            {'trigger': 'internal', 'source': 'B', 'dest': None},
        ]
        h = TestObject(states=state, initial=state[0], transitions=transitions, internal_id='---')
        self.helper_exc(h.table, h.staff)

    def test_warn_independent_state_transitions(self):
        others_init_states = [state for state in self.__states if state != self.__init]
        transitions = [
            {'trigger': 'to_self', 'source': others_init_states, 'dest': '='},
        ]
        h = TestObject(states=self.__states, initial=self.__init, transitions=transitions)
        self.helper_exc(h.table, h.staff)

    def test_warn_undefined_source_transitions(self):
        transitions = [
            {'trigger': 'Start->{}'.format(source), 'source': 'start', 'dest': source} for source in self.__states
        ]
        h = TestObject(states=self.__states, initial=self.__init, transitions=transitions)
        self.helper_exc(h.table, h.staff)

    def test_warn_undefined_dest_transitions(self):
        transitions = [
            {'trigger': 'Source->End', 'source': self.__states, 'dest': 'END'},
        ]
        h = TestObject(states=self.__states, initial=self.__init, transitions=transitions)
        self.helper_exc(h.table, h.staff)


    #定義に基づき、transition_tableの作成と遷移実行結果を比較するテスト実行する
    def helper_exc(self, st_table,staff, **kwargs):
        table, warn_list = self.helper_table(st_table, **kwargs)

        for t_source in table.columns:
            print("source state :{}".format(t_source))
            for t_event in table.index:
                print("  event :{}".format(t_event))
                t_dest = table[t_source][t_event]
                try:
                    #指定sourceで指定イベントを起こし結果を取得
                    result = staff.trigger(t_event, t_source)
                    s_source = result['source']
                    s_dest = result['dest']
                except ValueError as err:       # Machineは定義できてもイベントを起こすとエラーになる例外を取得
                    s_source = staff.state
                    s_dest = None
                    logging.warning(err)
                else:
                    self.helper_nomal_test(t_dest, s_dest, st_table.internal_id, st_table.undefined_id)
                finally:
                    print('', 'test',   'source : {},  dest : {}'.format(t_source, t_dest), sep='\t')
                    print('', 'actual', 'source : {},  dest : {}'.format(s_source, s_dest), sep='\t')
                    self.helper_warn_test(warn_list)
            print()

    #transition_tableとtable作成時のwarngingの取得
    def helper_table(self, st_table, **kargs):
        with warnings.catch_warnings(record=True) as w:
            table = st_table.get_table(**kargs)
            warn_list = []
            for warn in w:
                warn_list.append(warn)
        return table, warn_list

    #Exception発生しない場合における結果確認。transition_table値(t_dest)と実際の遷移結果(s_dest)を比較する
    def helper_nomal_test(self, t_dest, s_dest, internal_id, undefined_id):
        # internal result
        if s_dest is None:
            self.assertEqual(t_dest, internal_id)

        # undefined(NaN) result
        elif pd.isnull(s_dest):
            if pd.isnull(undefined_id):
                self.assertTrue(pd.isnull(t_dest))
            else:
                self.assertEqual(t_dest, internal_id)

        # other result
        else:
            self.assertEqual(t_dest, s_dest)

    #Warnging発生時のテスト(transitions_tableで定義されたwarning(UserWarning)を確認する)
    def helper_warn_test(self, warn_list):
        if len(warn_list) > 0:
            for warn in warn_list:
                if warn.category is not DeprecationWarning:             #transition_tableのUserWarningのみを入手したいため
                    self.assertEqual(warn.category, UserWarning)


if __name__ == '__main__':
    unittest.main()