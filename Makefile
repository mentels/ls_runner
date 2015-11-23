	.PHONY: compile get-deps update-deps clean deep-clean no-compile-rel \
	rel run test parse_and_plot

compile: get-deps
	./rebar compile

get-deps:
	./rebar get-deps

update-deps:
	./rebar update-deps

clean:
	./rebar clean

deep-clean: clean
	rm -rf deps/*/ebin/*

no-compile-rel:
	./relx -c _rel/relx.config

rel: compile no-compile-rel

run:
	./_rel/ls_runner/bin/ls_runner

dev:
	erl -pa ebin/ -pa deps/*/ebin/ -config config/sys.config \
	-args_file config/vm.args \
	-eval "application:ensure_all_started(ls_runner)"

test:
	mkdir -p /tmp/ct_log
	ct_run -pa deps/*/ebin -pa ebin/ -dir test/ -logdir /tmp/ct_log -noshell

rebar:
	wget -c https://github.com/rebar/rebar/wiki/rebar
	chmod +x rebar

parse_and_plot:
	python scripts/parse_ls_logs.py --open-plots

plot_mgr:
	./scripts/hdl_time_in_pktinf.py ~/Dropbox/MGR/testy/esl_env/_240h_regular_4sch
	./scripts/hdl_time_in_pktinf.py ~/Dropbox/MGR/testy/esl_env/_240h_regular_8sch
	./scripts/hdl_time_in_pktinf.py ~/Dropbox/MGR/testy/esl_env/_240h_ppsw_2sch
	./scripts/hdl_time_in_pktinf.py ~/Dropbox/MGR/testy/esl_env/_240h_ppsw_4sch
	./scripts/hdl_time_in_pktinf.py ~/Dropbox/MGR/testy/esl_env/_240h_ppsw_8sch
	./scripts/hdl_time_in_ts.py ~/Dropbox/MGR/testy/esl_env/

