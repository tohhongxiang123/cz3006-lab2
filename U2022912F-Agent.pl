/* Whether X, Y in the grid is visited. In the beginning, (0,0) is visited */
:- dynamic(visited/2).

/* position(x, y, orientation). Keeps track of the position of the agent */
:- dynamic(position/3).

/* Sets a new position for the agent, marking the new position as visited */
set_position(position(X, Y, Z)) :-
    call(position(OldX, OldY, OldZ)),
    retract(position(OldX, OldY, OldZ)),
    assertz(position(X, Y, Z)),
    /* When agent changes position, assert that the new position is visited */
    assertz(visited(X, Y)).

/* Check if X, Y, D is the current position */
current(X, Y, D) :-
    position(CurrentX, CurrentY, CurrentD),
    X = CurrentX, Y = CurrentY, D = CurrentD.

/* Whether the agent still has an arrow or not */
:- dynamic(hasarrow/0).
hasarrow.

/* Get the orientation of the agent after turning left */
get_left_orientation(X) :-
    position(_, _, Orientation),
    (
        Orientation == rnorth -> X = rwest ;
        Orientation == rwest -> X = rsouth ;
        Orientation == rsouth -> X = reast ;
        X = rnorth
    ).

/* Get the orientation of the agent after turning right */
get_right_orientation(X) :-
    position(_, _, Orientation),
    (
        Orientation == rnorth -> X = reast ;
        Orientation == reast -> X = rsouth ;
        Orientation == rsouth -> X = rwest ;
        X = rnorth
    ).

/* Make agent turn left with respect to its current orientation */
turn_left :-
    position(X, Y, Orientation),
    (
        Orientation == rnorth -> set_position(position(X,Y,rwest)) ;
        Orientation == rwest -> set_position(position(X,Y,rsouth)) ;
        Orientation == rsouth -> set_position(position(X,Y,reast)) ;
        set_position(position(X,Y,rnorth))
    ).

/* Make agent turn right with respect to its current orientation */
turn_right :-
    position(X, Y, Orientation),
    (
        Orientation == rnorth -> set_position(position(X,Y,reast)) ;
        Orientation == reast -> set_position(position(X,Y,rsouth)) ;
        Orientation == rsouth -> set_position(position(X,Y,rwest)) ;
        set_position(position(X,Y,rnorth))
    ).

/* Make agent move forward with respect to his current orientation */
move_forward :-
    position(Cx, Cy, Cz),
    get_forward_position(Cx, Cy, Cz, X, Y, Orientation),
    set_position(position(X, Y, Orientation)).

/* stench(X, Y) returns true if there is a stench at X, Y */
:- dynamic(stench/2).
/* tingle(X,Y) returns true if there is a tingle at X, Y */
:- dynamic(tingle/2).
/* glitter(X, Y) returns true if there is a glitter at X, Y */
:- dynamic(glitter/2).
/* scream(X,Y) returns true if there is scream at X, Y */
:- dynamic(scream/2).
/* bump(X,Y) returns true if there is a bump at X, Y */
:- dynamic(bump/2).
/* wumpus(X, Y) returns true if the wumpus is possibly at X,Y */
:- dynamic(wumpus/2).
/* wall(X, Y) returns true if there is a  wall at X,Y */
:- dynamic(wall/2).

/* adjacent(Xa, Ya, X, Y) returns (X, Y), a square adjacent to (Xa, Ya) */
adjacent(Xa, Ya, X, Y) :-
    X is Xa - 1, Y is Ya.
adjacent(Xa, Ya, X, Y) :-
    X is Xa + 1, Y is Ya.
adjacent(Xa, Ya, X, Y) :-
    X is Xa, Y is Ya - 1.
adjacent(Xa, Ya, X, Y) :-
    X is Xa, Y is Ya + 1.

wumpus(X, Y) :-
    /* A wumpus is at (X,Y) if we know there definitely is a wumpus at X,Y. Don't check further since there is only 1 wumpus */
    definitely_wumpus(X, Y), !.

wumpus(X, Y) :-
    /* A wumpus is at (X, Y) if there MIGHT be a wumpus at X, Y */
    maybe_wumpus(X, Y).

maybe_wumpus(X, Y) :-
    /* Wumpus might be at X, Y if it is adjacent to a stench, and X, Y is not already declared safe */
    stench(Xs, Ys), adjacent(Xs, Ys, X, Y), \+safe(X, Y).
    
/* Returns whether the wumpus is definitely at X,Y */
definitely_wumpus(X, Y) :-
    /* If we have 2 stenches, and a safe, we can conclude where the wumpus is */
    stench(X1, Y1),
    stench(X2, Y2),
    X1 > X2, Y1 > Y2,
    safe(X2, Y1), !,
    X is X1, Y is Y2.

definitely_wumpus(X, Y) :-
    stench(X1, Y1),
    stench(X2, Y2),
    X1 > X2, Y1 > Y2,
    safe(X1, Y2), !,
    X is X2, Y is Y1.

definitely_wumpus(X, Y) :-
    stench(X1, Y1),
    stench(X2, Y2),
    X1 < X2, Y1 > Y2,
    safe(X2, Y1), !,
    X is X1, Y is Y2.

definitely_wumpus(X, Y) :-
    stench(X1, Y1),
    stench(X2, Y2),
    X1 < X2, Y1 > Y2,
    safe(X1, Y2), !,
    X is X2, Y is Y1.

definitely_wumpus(X, Y) :-
    /* If X, Y is maybe wumpus, and the remaining diagonally adjacent squares are known to not be wumpus, 
    we can conclude X, Y is definitely a wumpus */
    maybe_wumpus(X, Y),
    FRx is X+1, FRy is Y+1,
    \+maybe_wumpus(FRx, FRy),
    FLx is X-1, FLy is Y+1,
    \+maybe_wumpus(FLx, FLy),
    BLx is X - 1, BLy is Y-1,
    \+maybe_wumpus(BLx, BLy),
    BRx is X+1, BRy is Y-1,
    \+maybe_wumpus(BRx, BRy).

/* Return whether a confundus portal is possibly at X,Y */
:- dynamic(confundus/2).
confundus(X, Y) :-
    /* Confundus portal is at X, Y if X, Y is adjacent to a tingle, X, Y is not visited, 
    not safe, and doesn't definitely contain a wumpus */
    tingle(Xt, Yt), adjacent(Xt, Yt, X, Y), \+visited(X, Y), \+safe(X, Y), \+definitely_wumpus(X, Y).
    
/* safe(X, Y) returns whether X, Y is safe (does not contain wumpus or portal) */
:- dynamic(safe/2).

/* Returns the number of coins the agent has collected */
:- dynamic(number_of_coins/1).
number_of_coins(0).

/* When reaching a position X, Y, we will update whether the adjacent squares are safe to visit 
If there is no stench or tingle on X, Y. We can safely assume that all adjacent squares are safe
*/
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
    assertz(wall(Fx, Fy)).

update_safe_positions :-
    scream(Cx,Cy),
    retract(scream(Cx, Cy)),
    retractall(stench(_,_)).

update_safe_positions :-
    true.

/* Shoot the wumpus if its definitely in front */
explore(L) :-
    position(Cx, Cy, Cz),
    stench(Cx, Cy),
    get_forward_position(Cx, Cy, Cz, X, Y, _),
    definitely_wumpus(X, Y),
    L = [shoot].

/* Shoot the wumpus if we are near it */
explore(L) :-
    position(Cx, Cy, Cz),
    stench(Cx, Cy),
    get_left_position(Cx, Cy, Cz, X, Y, _),
    definitely_wumpus(X, Y),
    L = [turnleft, shoot].

explore(L) :-
    position(Cx, Cy, Cz),
    stench(Cx, Cy),
    get_right_position(Cx, Cy, Cz, X, Y, _),
    definitely_wumpus(X, Y),
    L = [turnright, shoot].

/* If the current space has a coin, we pickup the coin */
explore(L) :-
    update_safe_positions,
    position(Cx, Cy, _),
    glitter(Cx, Cy),
    L = [pickup].

/* If glitter exists, we want to go to the glitter to pickup the coin */
explore(L) :-
    position(Cx, Cy, Cz),
    glitter(X, Y),
    generate_path_to(Cx, Cy, Cz, X, Y, L).

/* If the square infront is safe, we move forward */
explore(L) :-
    position(Cx, Cy, Cz),
    get_forward_position(Cx, Cy, Cz, X,Y,_),
    safe(X, Y), \+ visited(X, Y), \+wall(X, Y),
	L = [moveforward].

/* If the square to the right is safe, we turn right */
explore(L) :-
    position(Cx, Cy, Cz),
    get_right_position(Cx, Cy, Cz, X, Y, _),
    safe(X, Y), \+ visited(X, Y), \+wall(X, Y),
    L = [turnright, moveforward].

/* If the square to the left is safe, we turn left */
explore(L) :-
    position(Cx, Cy, Cz),
    get_left_position(Cx, Cy, Cz, X, Y, _),
    safe(X, Y), \+ visited(X, Y), \+wall(X,Y),
    L = [turnleft, moveforward].

/* If the square behind us is safe, we turn backwards */
explore(L) :-
    position(Cx, Cy, Cz),
    get_back_position(Cx, Cy, Cz, X, Y, _),
    safe(X, Y), \+ visited(X, Y), \+wall(X,Y),
    L = [turnright, turnright, moveforward].
    
/* If none of the squares directly adjacent to us are safe,
but there are still safe unvisited squares, we will find a path to it */
explore(L) :-
    safe(X,Y), \+visited(X, Y), \+wall(X,Y),
    position(Cx, Cy, Cz),
    find_closest_safe_unvisited(Cx, Cy, Cz, 20, L).

/* If there are no more unvisited nodes, go back to the start */
explore(L) :-
    position(Cx, Cy, Cz),
    generate_path_to(Cx, Cy, Cz, 0, 0, L).

/* Checks if L is a safe sequence of moves */
explore(L) :-
    current(X, Y, Z),
    check_safe(X, Y, Z, L).

check_safe(X, Y, _, []) :-
    safe(X, Y), \+wall(X, Y), !.

check_safe(X, Y, Z, [ToMove | Rest]) :-
    ToMove == moveforward,
    get_forward_position(X, Y, Z, NewX, NewY, NewZ),
    safe(X, Y), !,
    check_safe(NewX, NewY, NewZ, Rest).

check_safe(X, Y, Z, [ToMove | Rest]) :-
    ToMove == turnleft,
    get_left_position(X, Y, Z, _, _, NewZ),
    safe(X, Y), !,
    check_safe(X, Y, NewZ, Rest).

check_safe(X, Y, Z, [ToMove | Rest]) :-
    ToMove == turnright,
    get_right_position(X, Y, Z, _, _, NewZ),
    safe(X, Y), !,
    check_safe(X, Y, NewZ, Rest).

check_safe(X, Y, Z, [_ | Rest]) :-
    safe(X, Y), !, /* If the action to take does not change our position/orientation, we can ignore it */
    check_safe(X, Y, Z, Rest).

get_forward_position(OldX, OldY, Orientation, X,Y,Z) :-
    (
        Orientation == rnorth -> 
            Y is OldY+1, X is OldX, Z = Orientation ;
        Orientation == reast -> 
            Y is OldY, X is OldX+1, Z = Orientation ;
        Orientation == rsouth ->
            Y is OldY-1, X is OldX, Z = Orientation ;
        Y is OldY, X is OldX-1, Z = Orientation
    ).

get_left_position(OldX, OldY, Orientation, X, Y, Z) :-
    (
        Orientation == rnorth -> 
            Y is OldY, X is OldX - 1, Z = rwest ;
        Orientation == reast -> 
            Y is OldY + 1, X is OldX, Z = rnorth ;
        Orientation == rsouth -> 
            Y is OldY, X is OldX + 1, Z = reast ;
        Y is OldY - 1, X is OldX, Z = rsouth
    ).

get_right_position(OldX, OldY, Orientation,X,Y,Z) :-
    (
        Orientation == rnorth -> 
            Y is OldY, X is OldX + 1, Z = reast ;
        Orientation == reast -> 
            Y is OldY - 1, X is OldX, Z = rsouth ;
        Orientation == rsouth -> 
            Y is OldY, X is OldX - 1, Z = rwest ;
        Y is OldY + 1, X is OldX, Z = rnorth
    ).

get_back_position(OldX, OldY, Orientation, X,Y,Z) :-
    (
        Orientation == rnorth -> 
            Y is OldY-1, X is OldX, Z = rsouth ;
        Orientation == reast -> 
            Y is OldY, X is OldX-1, Z = rwest ;
        Orientation == rsouth -> 
            Y is OldY+1, X is OldX, Z = rnorth ;
        Y is OldY, X is OldX+1, Z = reast
    ).

find_closest_safe_unvisited(X, Y, Z, MaxDepth, L) :-
	path((X,Y), (GoalX, GoalY), ReversedPath),
    safe(GoalX, GoalY), \+visited(GoalX, GoalY), \+wall(GoalX, GoalY), !,
    length(ReversedPath, Length),
    ((Length =< MaxDepth) ; (Length > MaxDepth), !, fail),
    reverse(ReversedPath, [_ | Path]),
    generate_movements(X, Y, Z, Path, L).

generate_path_to(FromX, FromY, FromZ, ToX, ToY, L) :-
    ids((FromX, FromY), (ToX, ToY), 20, ReversedPath), !,
    reverse(ReversedPath, [_ | Path]),
    generate_movements(FromX, FromY, FromZ, Path, L).

ids(Node, (GoalX, GoalY), MaxDepth, Solution):-
	path(Node, (GoalX, GoalY), Solution),
    safe(GoalX, GoalY), \+wall(GoalX, GoalY), !,
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

/* Sets the position of the agent back to 0,0 */
reborn :- 
    assertz(hasarrow),
    reposition([on, off, off, off, off, off]).

move(moveforward, [_, _, _, _, Bump, _]) :-
    \+ (Bump == on),
    move_forward.

move(_, _) :-
    scream(X,Y),
    retract(scream(X,Y)).

move(_, _) :-
    bump(X,Y),
    retract(bump(X,Y)).

move(_, [_, Stench, _, _, _, _]) :-
    Stench == on,
    position(X,Y,_), assertz(stench(X, Y)).

move(_, [_, _, Tingle, _, _, _]) :-
    Tingle == on,
    position(X,Y,_), assertz(tingle(X, Y)).

move(_, [_, _, _, Glitter, _, _]) :-
    Glitter == on,
    position(X,Y,_), assertz(glitter(X, Y)).

move(_, [_, _, _, _, Bump, _]) :-
    Bump == on,
    position(X,Y,Z), assertz(bump(X, Y)),
    get_forward_position(X,Y,Z,Fx,Fy,_),
    assertz(wall(Fx,Fy)), 
    % assertz(visited(Fx, Fy)), 
    retract(safe(Fx, Fy)).
    
move(_, [_, _, _, _, _, Scream]) :-
    Scream == on,
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
    Scream == on,
    position(Cx, Cy, _),
    forall((stench(X, Y), \+ (Cx == X, Cy == Y)), (
        forall(adjacent(X, Y, Xn, Yn), (\+ tingle(Xn, Yn), \+ safe(Xn, Yn), assertz(safe(Xn, Yn))))
        % retractall(visited(X, Y))
    )),
    retract(stench(_,_)).

move(shoot, [_,_,_,_,_,_]) :-
    hasarrow,
    retractall(hasarrow).

move(_, _) :-
    update_safe_positions.

reposition(_) :-
    set_position(position(0, 0, rnorth)),
    retractall(visited(_, _)),
    retractall(stench(_, _)),
    retractall(tingle(_, _)),
    retractall(glitter(_, _)),
    retractall(safe(_, _)),
    assertz(visited(0, 0)),
    assertz(safe(0, 0)).
reposition([_, Stench, _, _, _, _]) :-
    Stench == on,
    position(X, Y, _),
    assertz(stench(X, Y)).
reposition([_, _, Tingle, _, _, _]) :-
    Tingle == on,
    position(X, Y, _),
    assertz(tingle(X, Y)).
reposition([_, _, _, Glitter, _, _]) :-
    Glitter == on,
    position(X, Y, _),
    assertz(glitter(X, Y)).
reposition([_, Stench, Tingle, _, _, _]) :-
    \+(Stench == on), \+(Tingle == on), update_safe_positions.

/* Starting variables */
position(0,0,rnorth).
visited(0, 0). 
safe(0,0).