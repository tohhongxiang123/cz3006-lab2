/* Whether X, Y in the grid is visited. In the beginning, (0,0) is visited */
:- dynamic(visited/2).

/* position(x, y, orientation) */
:- dynamic(position/3).
set_position(position(X, Y, Z)) :-
    call(position(OldX, OldY, OldZ)),
    retract(position(OldX, OldY, OldZ)),
    assertz(position(X, Y, Z)),
    /* When agent changes position, assert that the new position is visited */
    assertz(visited(X, Y)).

/* 
Sensory inputs, [Confounded, Stench, Tingle, Glitter, Bump, Scream]
*/

/* Whether the agent still has an arrow or not */
:- dynamic(hasarrow/0).
hasarrow.

/* Number of actions the agent has taken */
:- dynamic(number_of_actions/1).
number_of_actions(0).
add_number_of_actions :-
    number_of_actions(X),
    NewX is X+1,
    retract(number_of_actions(X)),
    assertz(number_of_actions(NewX)).

get_left_orientation(X) :-
    position(_, _, Orientation),
    (
        Orientation == north -> X = west ;
        Orientation == west -> X = south ;
        Orientation == south -> X = east ;
        X = north
    ).

get_right_orientation(X) :-
    position(_, _, Orientation),
    (
        Orientation == north -> X = east ;
        Orientation == east -> X = south ;
        Orientation == south -> X = west ;
        X = north
    ).

/* Agent turns left with respect to its current orientation */
turn_left :-
    position(X, Y, Orientation),
    (
        Orientation == north -> set_position(position(X,Y,west)) ;
        Orientation == west -> set_position(position(X,Y,south)) ;
        Orientation == south -> set_position(position(X,Y,east)) ;
        set_position(position(X,Y,north))
    ).

/* Agent turns right with respect to its current orientation */
turn_right :-
    position(X, Y, Orientation),
    (
        Orientation == north -> set_position(position(X,Y,east)) ;
        Orientation == east -> set_position(position(X,Y,south)) ;
        Orientation == south -> set_position(position(X,Y,west)) ;
        set_position(position(X,Y,north))
    ).

/* Moves the agent forward with respect to his current orientation */
move_forward :-
    position(Cx, Cy, Cz),
    get_forward_position(Cx, Cy, Cz, X, Y, Orientation),
    set_position(position(X, Y, Orientation)).

/* stench(X, Y) returns if there is a stench at X, Y */
:- dynamic(stench/2).
/* tingle(X,Y) returns if there is a tingle at X, Y */
:- dynamic(tingle/2).
/* glitter(X, Y) returns if there is a glitter at X, Y */
:- dynamic(glitter/2).
/* scream(X,Y) returns if there is scream at X, Y */
:- dynamic(scream/2).
/* bump(X,Y) returns if there is a bump at X, Y */
:- dynamic(bump/2).
/* Returns whether the wumpus is possibly at X,Y */
:- dynamic(wumpus/2).
/* Returns if wall is at X,Y */
:- dynamic(wall/2).

/* X, Y is a square adjacent to Xa, Ya */
adjacent(Xa, Ya, X, Y) :-
    X is Xa - 1, Y is Ya.
adjacent(Xa, Ya, X, Y) :-
    X is Xa + 1, Y is Ya.
adjacent(Xa, Ya, X, Y) :-
    X is Xa, Y is Ya - 1.
adjacent(Xa, Ya, X, Y) :-
    X is Xa, Y is Ya + 1.

wumpus(X, Y) :-
    definitely_wumpus(X, Y), !.
wumpus(X, Y) :-
    stench(Xs, Ys), adjacent(Xs, Ys, X, Y), \+visited(X, Y), \+safe(X, Y).
    
/* Returns whether the wumpus is definitely at X,Y */
definitely_wumpus(X, Y) :-
    stench(X1, Y1),
    stench(X2, Y2),
    X1 > X2, Y1 > Y2,
    safe(X2, Y1),
    X is X1, Y is Y2.

definitely_wumpus(X, Y) :-
    stench(X1, Y1),
    stench(X2, Y2),
    X1 > X2, Y1 > Y2,
    safe(X1, Y2),
    X is X2, Y is Y1.

definitely_wumpus(X, Y) :-
    stench(X1, Y1),
    stench(X2, Y2),
    X1 < X2, Y1 > Y2,
    safe(X2, Y1),
    X is X1, Y is Y2.

definitely_wumpus(X, Y) :-
    stench(X1, Y1),
    stench(X2, Y2),
    X1 < X2, Y1 > Y2,
    safe(X1, Y2),
    X is X2, Y is Y1.

/* Return whether a confundus portal is possibly at X,Y */
:- dynamic(confundus/2).
confundus(X, Y) :-
    tingle(Xt, Yt), adjacent(Xt, Yt, X, Y), \+visited(X, Y), \+safe(X, Y), \+definitely_wumpus(X, Y).
    
:- dynamic(safe/2).
:- dynamic(number_of_coins/1).
number_of_coins(0).

/* If current square has no stench or tingle, mark all adjacent squares safe */
% update_safe_positions :-
%     position(X, Y, Z),
%     \+ stench(X,Y), \+ tingle(X,Y),
%     get_left_position(X, Y, Z, Lx, Ly, _),
%     assertz(safe(Lx, Ly)),
%     get_right_position(X, Y, Z, Rx, Ry, _),
%     assertz(safe(Rx, Ry)),
%     get_back_position(X, Y, Z, Bx, By, _),
%     assertz(safe(Bx, By)),
%     get_forward_position(X, Y, Z, Fx, Fy, _),
%     assertz(safe(Fx, Fy)) ; true.

update_safe_positions :-
    position(X, Y, Z),
    \+stench(X, Y), \+tingle(X, Y),
    get_left_position(X, Y, Z, NewX, NewY, _),
    \+safe(NewX, NewY), assertz(safe(NewX, NewY)).
update_safe_positions :-
    position(X, Y, Z),
    \+stench(X, Y), \+tingle(X, Y),
    get_right_position(X, Y, Z, NewX, NewY, _),
    \+safe(NewX, NewY), assertz(safe(NewX, NewY)).
update_safe_positions :-
    position(X, Y, Z),
    \+stench(X, Y), \+tingle(X, Y),
    get_forward_position(X, Y, Z, NewX, NewY, _),
    \+safe(NewX, NewY), assertz(safe(NewX, NewY)).
update_safe_positions :-
    position(X, Y, Z),
    \+stench(X, Y), \+tingle(X, Y),
    get_back_position(X, Y, Z, NewX, NewY, _),
    \+safe(NewX, NewY), assertz(safe(NewX, NewY)).

update_safe_positions :-
    position(X,Y,Z),
    bump(X,Y),
    get_forward_position(X,Y,Z,Fx,Fy,_),
    assertz(wall(Fx, Fy)),
    assertz(visited(Fx,Fy)).

update_safe_positions :-
    scream(Cx,Cy),
    retract(scream(Cx, Cy)),
    retractall(stench(_,_)) ; true.

update_safe_positions :-
    true.


/* If the current space has a coin, we pickup the coin */
explore(L) :-
    update_safe_positions,
    position(Cx, Cy, _),
    glitter(Cx, Cy), !,
    L = [pickup], write("Here 13"), nl.

/* Shoot the wumpus if its definitely in front */
explore(L) :-
    position(Cx, Cy, Cz),
    stench(Cx, Cy),
    get_forward_position(Cx, Cy, Cz, X, Y, _),
    definitely_wumpus(X, Y), !,
    L = [shoot], write("Here 12"), nl.

explore(L) :-
    position(Cx, Cy, Cz),
    stench(Cx, Cy),
    get_left_position(Cx, Cy, Cz, X, Y, _),
    definitely_wumpus(X, Y), !,
    L = [turnleft, shoot], write("Here 11"), nl.

explore(L) :-
    position(Cx, Cy, Cz),
    stench(Cx, Cy),
    get_right_position(Cx, Cy, Cz, X, Y, _),
    definitely_wumpus(X, Y), !,
    L = [turnright, shoot], write("Here 10"), nl.

/* Turn right if wall in front and not visited */
explore(L) :-
    position(Cx, Cy, Cz),
    bump(Cx, Cy),
    get_forward_position(Cx, Cy, Cz, X, Y, _),
    retract(safe(X, Y)),
    get_right_position(Cx, Cy, Cz, X, Y, _),
    safe(X, Y), \+visited(X, Y), !,
    L = [turnright, moveforward], write("Here 9"), nl.

/* Turn left if wall in frnot and not visited */
explore(L) :-
    position(Cx, Cy, Cz),
    bump(Cx, Cy),
    get_left_position(Cx, Cy, Cz, X, Y, _),
    safe(X, Y), \+visited(X, Y), !,
    L = [turnleft, moveforward], write("Here 8"), nl.

/* If glitter exists, we want to go to the glitter */
explore(L) :-
    position(Cx, Cy, Cz),
    glitter(X, Y), !,
    generate_path_to(Cx, Cy, Cz, X, Y, L),!, write("Here 7"), nl.

/* If the square infront is safe, we move forward */
explore(L) :-
    position(Cx, Cy, Cz),
    get_forward_position(Cx, Cy, Cz, X,Y,_),
    safe(X, Y), \+ visited(X, Y), !,
	L = [moveforward].

/* If the square to the right is safe, we turn right */
explore(L) :-
    position(Cx, Cy, Cz),
    get_right_position(Cx, Cy, Cz, X, Y, _),
    safe(X, Y), \+ visited(X, Y),  !,
    L = [turnright, moveforward].

/* If the square to the left is safe, we turn left */
explore(L) :-
    position(Cx, Cy, Cz),
    get_left_position(Cx, Cy, Cz, X, Y, _),
    safe(X, Y), \+ visited(X, Y), !,
    L = [turnleft, moveforward].

explore(L) :-
    position(Cx, Cy, Cz),
    get_back_position(Cx, Cy, Cz, X, Y, _),
    safe(X, Y), \+ visited(X, Y), !,
    L = [turnright, turnright, moveforward].

% explore(L) :-
%     safe(X, Y), \+visited(X, Y), \+wall(X,Y), !,
%     position(Cx, Cy, Cz),
%     generate_path_to(Cx, Cy, Cz, X, Y, L), write("Here 3"), nl.
    
explore(L) :-
    safe(X,Y), \+visited(X, Y), !,
    position(Cx, Cy, Cz),
    find_closest_safe_unvisited(Cx, Cy, Cz, 20, L), !.

% explore(L) :-
%     safe(X, Y), \+visited(X, Y), !,
%     position(Cx, Cy, Cz),
%     generate_path_to(Cx, Cy, Cz, X, Y, L), write("Here 2"), nl, format("~w ~w ~w ~w", [Cx, Cy, X, Y]), nl.

/* If there are no more unvisited nodes, go back to the start */
explore(L) :-
    position(Cx, Cy, Cz),
    generate_path_to(Cx, Cy, Cz, 0, 0, L).

get_forward_position(OldX, OldY, Orientation, X,Y,Z) :-
    (
        Orientation == north -> 
            Y is OldY+1, X is OldX, Z = Orientation ;
        Orientation == east -> 
            Y is OldY, X is OldX+1, Z = Orientation ;
        Orientation == south ->
            Y is OldY-1, X is OldX, Z = Orientation ;
        Y is OldY, X is OldX-1, Z = Orientation
    ).

get_left_position(OldX, OldY, Orientation, X, Y, Z) :-
    (
        Orientation == north -> 
            Y is OldY, X is OldX - 1, Z = west ;
        Orientation == east -> 
            Y is OldY + 1, X is OldX, Z = north ;
        Orientation == south -> 
            Y is OldY, X is OldX + 1, Z = east ;
        Y is OldY - 1, X is OldX, Z = south
    ).

get_right_position(OldX, OldY, Orientation,X,Y,Z) :-
    (
        Orientation == north -> 
            Y is OldY, X is OldX + 1, Z = east ;
        Orientation == east -> 
            Y is OldY - 1, X is OldX, Z = south ;
        Orientation == south -> 
            Y is OldY, X is OldX - 1, Z = west ;
        Y is OldY + 1, X is OldX, Z = north
    ).

get_back_position(OldX, OldY, Orientation, X,Y,Z) :-
    (
        Orientation == north -> 
            Y is OldY-1, X is OldX, Z = south ;
        Orientation == east -> 
            Y is OldY, X is OldX-1, Z = west ;
        Orientation == south -> 
            Y is OldY+1, X is OldX, Z = north ;
        Y is OldY, X is OldX+1, Z = east
    ).

/* Y = |X| */
abs(X, Y) :- X < 0, Y is -X.
abs(X, X) :- X >= 0, !.

/* Returns D the euclidean distance between (X1, Y1) and (X2, Y2) */
distance(X1, X2, Y1, Y2, D) :-
    D is sqrt((X2-X1)^2 + (Y2-Y1)^2).

find_closest_safe_unvisited(X, Y, Z, MaxDepth, L) :-
	path((X,Y), (GoalX, GoalY), ReversedPath),
    safe(GoalX, GoalY), \+visited(GoalX, GoalY), !,
    length(ReversedPath, Length),
    ((Length =< MaxDepth, !) ; (Length > MaxDepth), !, fail),
    reverse(ReversedPath, [_ | Path]),
    generate_movements(X, Y, Z, Path, L), !.

generate_path_to(FromX, FromY, FromZ, ToX, ToY, L) :-
    ids((FromX, FromY), (ToX, ToY), 20, ReversedPath), !,
    reverse(ReversedPath, [_ | Path]),
    generate_movements(FromX, FromY, FromZ, Path, L).

ids(Node, (GoalX, GoalY), MaxDepth, Solution):-
	path(Node, (GoalX, GoalY), Solution),
    safe(GoalX, GoalY), !,
    length(Solution, Length),
    ( (Length =< MaxDepth) ; (Length > MaxDepth), !, fail).

path(Node, Node, [Node]).
path((FromX, FromY), (ToX, ToY), [(ToX, ToY)|Path]) :- 
    path((FromX, FromY), (X, Y), Path),
    safe(X, Y), adjacent(X,Y, ToX, ToY), \+wall(X,Y),
    \+ member((ToX, ToY), Path).

generate_movements(_, _, _, [], L) :-
    L = [].
generate_movements(FromX, FromY, _, [(FromX, FromY)], L) :-
    L = [].

generate_movements(FromX, FromY, FromZ, [(HeadX, HeadY) | Path], L) :-
    get_forward_position(FromX, FromY, FromZ, NewX, NewY, NewZ),
    NewX == HeadX, NewY == HeadY,
    generate_movements(NewX, NewY, NewZ, Path, L2),
    L = [moveforward | L2].

generate_movements(FromX, FromY, FromZ, [(HeadX, HeadY) | Path], L) :-
    get_left_position(FromX, FromY, FromZ, NewX, NewY, NewZ),
    NewX == HeadX, NewY == HeadY,
    generate_movements(NewX, NewY, NewZ, Path, L2),
    L = [turnleft, moveforward | L2].

generate_movements(FromX, FromY, FromZ, [(HeadX, HeadY) | Path], L) :-
    get_right_position(FromX, FromY, FromZ, NewX, NewY, NewZ),
    NewX == HeadX, NewY == HeadY,
    generate_movements(NewX, NewY, NewZ, Path, L2),
    L = [turnright, moveforward | L2].

generate_movements(FromX, FromY, FromZ, [(HeadX, HeadY) | Path], L) :-
    get_back_position(FromX, FromY, FromZ, NewX, NewY, NewZ),
    NewX == HeadX, NewY == HeadY,
    generate_movements(NewX, NewY, NewZ, Path, L2),
    L = [turnright, turnright, moveforward | L2].

% generate_path_to(FromX, FromY, FromZ, ToX, ToY, L) :-
%     generate_path_to(FromX, FromY, FromZ, ToX, ToY, L, 30).

% generate_path_to(_,_,_,_,_,L,DepthRemaining) :-
%     DepthRemaining == 0, !, L = [].

% generate_path_to(FromX, FromY, _, ToX, ToY, L, _) :-
%     distance(FromX, ToX, FromY, ToY, TotalRequiredOffset),
%     TotalRequiredOffset < 1, !, % Using inequality due to comparing floats
%     L = [].

% generate_path_to(FromX, FromY, _, _, _, L, _) :-
%     safe(FromX, FromY), glitter(FromX, FromY),
%     L = [pickup].

% generate_path_to(FromX, FromY, FromZ, ToX, ToY, L, DepthRemaining) :-
%     distance(FromX, ToX, FromY, ToY, TotalRequiredOffset),
%     get_forward_position(FromX, FromY, FromZ, NewX, NewY, NewZ),
%     safe(NewX, NewY), glitter(NewX, NewY),
%     distance(NewX, ToX, NewY, ToY, NewTotalOffset),
%     NewTotalOffset < TotalRequiredOffset, !,
%     NewDepthRemaining is DepthRemaining - 1,
%     generate_path_to(NewX, NewY, NewZ, ToX, ToY, L2, NewDepthRemaining),
%     L = [moveforward, pickup | L2].

% generate_path_to(FromX, FromY, FromZ, ToX, ToY, L, DepthRemaining) :-
%     distance(FromX, ToX, FromY, ToY, TotalRequiredOffset),
%     get_forward_position(FromX, FromY, FromZ, NewX, NewY, NewZ),
%     safe(NewX, NewY),
%     distance(NewX, ToX, NewY, ToY, NewTotalOffset),
%     NewTotalOffset < TotalRequiredOffset, !,
%     NewDepthRemaining is DepthRemaining - 1,
%     generate_path_to(NewX, NewY, NewZ, ToX, ToY, L2, NewDepthRemaining),
%     L = [moveforward | L2].

% generate_path_to(FromX, FromY, FromZ, ToX, ToY, L, DepthRemaining) :-
%     distance(FromX, ToX, FromY, ToY, TotalRequiredOffset),
%     get_left_position(FromX, FromY, FromZ, NewX, NewY, NewZ),
%     safe(NewX, NewY),
%     distance(NewX, ToX, NewY, ToY, NewTotalOffset),
%     NewTotalOffset < TotalRequiredOffset, !,
%     NewDepthRemaining is DepthRemaining - 1,
%     generate_path_to(FromX, FromY, NewZ, ToX, ToY, L2, NewDepthRemaining),
%     L = [turnleft | L2], !.

% generate_path_to(FromX, FromY, FromZ, ToX, ToY, L, DepthRemaining) :-
%     distance(FromX, ToX, FromY, ToY, TotalRequiredOffset),
%     get_right_position(FromX, FromY, FromZ, NewX, NewY, NewZ),
%     safe(NewX, NewY),
%     distance(NewX, ToX, NewY, ToY, NewTotalOffset),
%     NewTotalOffset < TotalRequiredOffset, !,
%     NewDepthRemaining is DepthRemaining - 1,
%     generate_path_to(FromX, FromY, NewZ, ToX, ToY, L2, NewDepthRemaining),
%     L = [turnright | L2], !.

% generate_path_to(FromX, FromY, FromZ, _, _, L, _) :-
%     get_forward_position(FromX, FromY, FromZ, NewX, NewY, _),
%     safe(NewX, NewY), \+visited(NewX, NewY),
%     L = [moveforward], !.

% generate_path_to(FromX, FromY, FromZ, _, _, L, _) :-
%     get_left_position(FromX, FromY, FromZ, NewX, NewY, _),
%     safe(NewX, NewY), \+visited(NewX, NewY),
%     L = [turnleft, moveforward], !.

% generate_path_to(FromX, FromY, FromZ, _, _, L, _) :-
%     get_right_position(FromX, FromY, FromZ, NewX, NewY, _),
%     safe(NewX, NewY), \+visited(NewX, NewY),
%     L = [turnright, moveforward], !.

% generate_path_to(FromX, FromY, FromZ, _, _, L, _) :-
%     get_back_position(FromX, FromY, FromZ, NewX, NewY, _),
%     safe(NewX, NewY),
%     L = [turnright, turnright, moveforward], !.

% generate_path_to(FromX, FromY, FromZ, ToX, ToY, L, DepthRemaining) :-
%     get_forward_position(FromX, FromY, FromZ, NewX, NewY, NewZ),
%     safe(NewX, NewY),
%     NewDepthRemaining is DepthRemaining - 1,
%     generate_path_to(NewX, NewY, NewZ, ToX, ToY, L2, NewDepthRemaining),
%     L = [moveforward | L2].

% generate_path_to(FromX, FromY, FromZ, ToX, ToY, L, DepthRemaining) :-
%     get_left_position(FromX, FromY, FromZ, NewX, NewY, NewZ),
%     safe(NewX, NewY),
%     NewDepthRemaining is DepthRemaining - 1,
%     generate_path_to(NewX, NewY, NewZ, ToX, ToY, L2, NewDepthRemaining),
%     L = [turnleft, moveforward | L2].

% generate_path_to(FromX, FromY, FromZ, ToX, ToY, L, DepthRemaining) :-
%     get_right_position(FromX, FromY, FromZ, NewX, NewY, NewZ),
%     safe(NewX, NewY),
%     NewDepthRemaining is DepthRemaining - 1,
%     generate_path_to(NewX, NewY, NewZ, ToX, ToY, L2, NewDepthRemaining),
%     L = [turnright, moveforward | L2].

% generate_path_to(FromX, FromY, FromZ, ToX, ToY, L, DepthRemaining) :-
%     get_back_position(FromX, FromY, FromZ, NewX, NewY, NewZ),
%     safe(NewX, NewY),
%     NewDepthRemaining is DepthRemaining - 1,
%     generate_path_to(NewX, NewY, NewZ, ToX, ToY, L2, NewDepthRemaining),
%     L = [turnright, turnright, moveforward | L2].

% /* Should not be reached */
% generate_path_to(_, _, _, _, _, L, _) :-
%     L = [], !.

/* Sets the position of the agent back to 0,0 */
reborn :- 
    assertz(hasarrow),
    reposition([true, false, false, false, false, false]).

move(moveforward, [_, _, _, _, Bump, _]) :-
    \+ Bump,
    move_forward.

move(_, _) :-
    scream(X,Y),
    retract(scream(X,Y)).

move(_, _) :-
    bump(X,Y),
    retract(bump(X,Y)).

% move(_, [Confounded, _, _, _, _, _]) :-
%     Confounded,
%     position(X,Y,_), assertz(confundus(X, Y)).

move(_, [_, Stench, _, _, _, _]) :-
    Stench,
    position(X,Y,_), assertz(stench(X, Y)).

move(_, [_, _, Tingle, _, _, _]) :-
    Tingle,
    position(X,Y,_), assertz(tingle(X, Y)).

move(_, [_, _, _, Glitter, _, _]) :-
    Glitter,
    position(X,Y,_), assertz(glitter(X, Y)).

move(_, [_, _, _, _, Bump, _]) :-
    Bump,
    position(X,Y,Z), assertz(bump(X, Y)),
    get_forward_position(X,Y,Z,Fx,Fy,_),
    assertz(wall(Fx,Fy)), assertz(visited(Fx, Fy)), retract(safe(Fx, Fy)).
    
move(_, [_, _, _, _, _, Scream]) :-
    Scream,
    position(X,Y,_), assertz(scream(X, Y)).

move(turnleft, _) :-
    turn_left.

move(turnright, _) :-
    turn_right.

move(pickup, _) :-
    glitter(X, Y),
    number_of_coins(N),
    N1 is N + 1,
    retract(number_of_coins(N)),
    assertz(number_of_coins(N1)),
    retract(glitter(X,Y)).

move(shoot, [_,_,_,_,_,Scream]) :-
    hasarrow,
    Scream,
    forall(stench(X, Y), retractall(visited(X, Y))),
    retract(stench(_,_)) ; retract(hasarrow).

move(_, _) :-
    update_safe_positions.

reposition(_) :-
    set_position(position(0, 0, north)),
    retractall(visited(_, _)),
    retractall(stench(_, _)),
    retractall(tingle(_, _)),
    retractall(glitter(_, _)),
    retractall(safe(_, _)),
    assertz(visited(0, 0)),
    assertz(safe(0, 0)).

reposition([_, Stench, _, _, _, _]) :-
    Stench,
    position(X, Y, _),
    assertz(stench(X, Y)).
reposition([_, _, Tingle, _, _, _]) :-
    Tingle,
    position(X, Y, _),
    assertz(tingle(X, Y)).
reposition([_, _, _, Glitter, _, _]) :-
    Glitter,
    position(X, Y, _),
    assertz(glitter(X, Y)).
reposition([_, Stench, Tingle, _, _, _]) :-
    \+Stench, \+Tingle, update_safe_positions.

/* Check if X, Y, D is the current position */
current(X, Y, D) :-
    position(CurrentX, CurrentY, CurrentD),
    X = CurrentX, Y = CurrentY, D = CurrentD.

/* Starting variables */
position(0,0,north).
visited(0, 0). 
safe(0,0).