from transitions import Machine, MachineError
from transitions_table import TransitionsTable
import pandas as pd
import logging

class Staff(Machine):
	def __init__(self, default_invalid=pd.np.nan, default_internal='[internal]', **kwargs):
		s_kargs = {
			'auto_transitions':False,
			'ordered_transitions':False
		}
		args = [self]
		s_kargs.update(kwargs)

		super().__init__(*args, **s_kargs)
		self.__invalid = default_invalid
		self.__internal = default_internal

	def trigger(self, event, state=None, *args, **kwargs):
		source = self.state if state is None else state
		transition = {'trigger': event, 'source': source}
		try:
			self.set_state(source)
			if getattr(self.model, event)(*args, **kwargs):				# イベント発生
				if source == self.state:
					dest = self.get_transitions(event, source)[0].dest  # 自己遷移と内部遷移の判定のため
				else:
					dest = self.state
			else :
				dest = self.__invalid
		except MachineError as err:
			logging.info('Machine Transition Exception:{}'.format(err))
			dest = self.__invalid
		transition['dest'] = dest

		return transition

class TestObject(object):
	def __init__(self, states=None, initial=None, transitions=None, ordered_transitions=None, auto_transitions=None,
				 internal_id=None, undefined_id=None, is_warn=None):
		staff_kwargs = {}
		if states is not None: staff_kwargs["states"] = states
		if initial is not None: staff_kwargs["initial"] = initial
		if transitions is not None: staff_kwargs["transitions"] = transitions
		if ordered_transitions is not None: staff_kwargs["ordered_transitions"] = ordered_transitions
		if auto_transitions is not None: staff_kwargs["auto_transitions"] = auto_transitions
		if internal_id is not None: staff_kwargs["default_internal"] = internal_id
		if undefined_id is not None: staff_kwargs["default_invalid"] = undefined_id

		self.__staff = Staff(**staff_kwargs)

		table_kwargs = {}
		if internal_id is not None: table_kwargs["internal_id"] = internal_id
		if undefined_id is not None: table_kwargs["undefined_id"] = undefined_id

		table_args = [self.__staff]
		self.__st_table = TransitionsTable(*table_args, **table_kwargs)

		self.__gt_kwargs = {}
		if is_warn is not None: self.__gt_kwargs["is_warn"] = is_warn

	@property
	def staff(self):
		return self.__staff

	@property
	def table(self):
		return self.__st_table