import pandas as pd
import warnings

class TransitionsTable:
	def __init__(self, machine, internal_id='[internal]', undefined_id=pd.np.nan, *args, **kwargs):
		self.__machine = machine
		self.__internal_id = internal_id  			# 内部遷移時の文字列
		self.__undefined_id = undefined_id  		# 遷移なし時の文字列
		self.__transitions_list = []  				# list(dict)形式でevent, source, destを格納する
		self.__source_list = []  					# list(str)形式でTransitionsで設定された遷移前状態を格納する
		self.__dest_list = []  						# list(str)形式でTransitionsで設定された遷移後状態を格納する
		self.__state_list = [self.__internal_id]  	# list(str)形式でStateで設定された状態を格納する
		self.__undefined_state = []  				# Transitionsで定義してあってStateで定義していない状態
		self.__undefined_transitions = []  			# Stateで定義してあってTransitions(source/dest)で定義していない状態

	def __call__(self, machine):
		self.__init__(machine)

	# 遷移の一覧を取得
	def __get_transitions(self):
		events = [event_name for event_name in self.__machine.events.keys()]
		for event in events:
			transitions = self.__machine.get_transitions(event)
			for t in transitions:
				source, dest = self.__reform_source_and_dest(t.source, t.dest)
				dict = {'event': event, 'source': source, 'dest': dest}
				self.__transitions_list.append(dict)

	# 特殊な遷移設定に対する置き換え処理
	def __reform_source_and_dest(self, raw_source, raw_dest):
		source = raw_source if raw_source != '*' else self.__state_list
		if raw_dest == '=':
			dest = source
		elif raw_dest is None:
			dest = self.__internal_id
		else:
			dest = raw_dest
		return source, dest

	# 各種判定に必要な状態の一覧を取得
	def __get_control_states(self):
		source_list = [t_source['source'] for t_source in self.__transitions_list]
		self.__source_list = sorted(set(source_list))  # 重複削除

		dest_list = [t_dict['dest'] for t_dict in self.__transitions_list if t_dict['dest'] != self.__internal_id]
		self.__dest_list = sorted(set(dest_list))  # 重複削除

		undefined_source = [state for state in self.__source_list if not state in self.__state_list]
		undefined_dest = [state for state in self.__dest_list if not state in self.__state_list]
		self.__undefined_state = sorted(set(undefined_source + undefined_dest))

		self.__undefined_transitions = [state for state in self.__state_list \
										if ((not state in self.__dest_list) and (not state in self.__source_list))]

	@property
	def internal_id(self):
		return self.__internal_id

	@property
	def undefined_id(self):
		return self.__undefined_id

	# 状態遷移表をpandas.DataFrame形式で出力する（列：状態、行：イベント）
	def get_table(self, is_warning=True):
		self.__state_list = [state for state in self.__machine.states.keys()]
		self.__get_transitions()
		self.__get_control_states()

		df_state = pd.DataFrame(columns=sorted(set(self.__state_list + self.__dest_list)))
		if len(self.__transitions_list) >= 1:
			df_trans = pd.DataFrame(self.__transitions_list).set_index('event')
			pv_trans = df_trans.pivot(values='dest', columns='source')
			table = pd.concat([pv_trans, df_state], sort=True)
		else:
			table = df_state  # stateのみの場合(eventがなくdf_transを作成できないので)table作成できるようにするため

		if self.__undefined_id != pd.np.nan:
			if (self.__internal_id in self.__state_list) or (self.__internal_id in self.__undefined_state):
				raise ValueError('引数internal_idに状態元/遷移先に含まれる状態名を指定することはできません')
			if (self.__undefined_id in self.__state_list) or (self.__internal_id in self.__undefined_state):
				raise ValueError('引数undefined_idに状態元/遷移先に含まれる状態名を指定することはできません')
			table = table.replace({pd.np.nan: self.__undefined_id})

		if is_warning:
			if len(self.__undefined_state) >= 1:
				warnings.warn("状態引数(state)に定義されていない状態への遷移があります : {}".format(self.__undefined_state), category=UserWarning)
			if len(self.__undefined_transitions) >= 1:
				warnings.warn("一つも遷移設定のない状態(state)があります : {}".format(self.__undefined_transitions), category=UserWarning)
		return table

