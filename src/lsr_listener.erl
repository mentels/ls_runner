-module(lsr_listener).
-behaviour(gen_server).
-define(SERVER, ?MODULE).

%% ------------------------------------------------------------------
%% API Function Exports
%% ------------------------------------------------------------------

-export([start_link/0]).

%% ------------------------------------------------------------------
%% gen_server Function Exports
%% ------------------------------------------------------------------

-export([init/1, handle_call/3, handle_cast/2, handle_info/2,
         terminate/2, code_change/3]).

%% ------------------------------------------------------------------
%% Records & Includes
%% ------------------------------------------------------------------

-record(state, {socket}).

-include("lsr_logger.hrl").

%% ------------------------------------------------------------------
%% API Function Definitions
%% ------------------------------------------------------------------

start_link() ->
    gen_server:start_link({local, ?SERVER}, ?MODULE, [], []).

%% ------------------------------------------------------------------
%% gen_server Function Definitions
%% ------------------------------------------------------------------

init([]) ->
    SockOpts = [{active, true}, binary],
    {ok, Port} = application:get_env(port),
    {ok, Sock} = gen_udp:open(Port, SockOpts),
    {ok, #state{socket = Sock}}.

handle_call(_Request, _From, State) ->
    {reply, ok, State}.

handle_cast(_Msg, State) ->
    {noreply, State}.

handle_info({udp, Socket, IP, InPortNo, Packet},
            #state{socket = Socket} = State) ->
    handle_request(Packet, Socket, IP, InPortNo),
    {noreply, State};
handle_info(_Info, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.

%% ------------------------------------------------------------------
%% Internal Function Definitions
%% ------------------------------------------------------------------

handle_request(<<"prepare/", RunId/binary>>, Socket, IP,PortNo) ->
    lager:info([{ls, x}], "[LSR] Got request to prepare for run ~p", [RunId]),
    prepare(Socket, IP, PortNo);
handle_request(<<"stop/", RunId/binary>>, Socket, IP, PortNo) ->
    lager:info([{ls, x}], "[LSR] Got request to stop run  ~p", [RunId]),
    stop(Socket, IP, PortNo, RunId).


prepare(Socket, IP, PortNo) ->
    ok = file:delete("log/notice.log"),
    {ok, _} = application:ensure_all_started(ls),
    lager:info([{ls, x}], "[LSR] notice.log deleted and ls started"),
    ok = gen_udp:send(Socket, IP, PortNo, <<"ready">>).

stop(Socket, IP, PortNo, RunId) ->
    [ok = application:stop(App) || App <- [ls, exometer, exometer_core]],
    RunLogDir = filename:join(["log", binary_to_list(RunId)]),
    ok = file:make_dir(RunLogDir),
    {ok, _} = file:copy("log/notice.log",
                        filename:join([RunLogDir, "notice.log"])),
    lager:info([{ls, x}], "[LSR] notice.log copied to ~p and ls stopped",
               [RunLogDir]),
    ok = gen_udp:send(Socket, IP, PortNo, <<"stopped">>).










