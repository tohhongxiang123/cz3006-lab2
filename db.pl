/* Max number of actions */
max_number_of_actions(50).

/* position(x, y, orientation) */
:- dynamic(position/3).
set_position(position(X, Y, Z)) :-
    call(position(OldX, OldY, OldZ)),
    retract(position(OldX, OldY, OldZ)),
    assertz(position(X, Y, Z)),
    /* When agent changes position, assert that the new position is visited */
    assertz(visited(X, Y)).

/* Whether X, Y in the grid is visited. In the beginning, (0,0) is visited */
:- dynamic(visited/2).

/* 
Sensory inputs, [confounded, stench, tingle, glitter, bump, scream] 
confounded is true at the start of the game
*/
:- dynamic(senses/6).
senses(true, false, false, false, false, false).

set_senses(senses(Confounded, Stench, Tingle, Glitter, Bump, Scream)) :-
    call(senses(X1,X2,X3,X4,X5,X6)),
    retract(senses(X1,X2,X3,X4,X5,X6)),
    assertz(senses(Confounded, Stench, Tingle, Glitter, Bump, Scream)).

/* A list of the nodes we travelled */
:- dynamic(path/1).
path([position(0,0)]).

/* Add the new node to the path */
add_path(ToAdd) :- 
    path(OldPath),
    append(OldPath, [ToAdd], NewPath),
    call(path(OldX)),
    retract(path(OldX)),
    assertz(path(NewPath)).

/* Pop the latest node in the path */
without_last([_], []).
without_last([X|Xs], [X|WithoutLast]) :- 
    without_last(Xs, WithoutLast).

get_last([X], X).
get_last([_ | T], Last) :-
    get_last(T, Last).

pop_path(Popped) :-
    path(OldPath),
    get_last(OldPath, Popped),
    without_last(OldPath, NewPath),
    retract(path(OldPath)),
    assertz(path(NewPath)).

/* Whether the agent still has an arrow or not */
hasarrow.

/* Number of actions the agent has taken */
:- dynamic(number_of_actions/1).
number_of_actions(0).
add_number_of_actions :-
    number_of_actions(X),
    NewX is X+1,
    retract(number_of_actions(X)),
    assertz(number_of_actions(NewX)).

/* Agent turns left with respect to its current orientation */
turn_left :-
    add_number_of_actions,
    position(X, Y, Orientation),
    (
        Orientation == north -> set_position(position(X,Y,west)) ;
        Orientation == west -> set_position(position(X,Y,south)) ;
        Orientation == south -> set_position(position(X,Y,east)) ;
        set_position(position(X,Y,north))
    ).

/* Agent turns right with respect to its current orientation */
turn_right :-
    add_number_of_actions,
    position(X, Y, Orientation),
    (
        Orientation == north -> set_position(position(X,Y,east)) ;
        Orientation == east -> set_position(position(X,Y,south)) ;
        Orientation == south -> set_position(position(X,Y,west)) ;
        set_position(position(X,Y,north))
    ).

/* Moves the agent forward with respect to his current orientation */
move_forward :-
    add_number_of_actions,
    get_forward_position(X, Y, Orientation),
    set_position(position(X, Y, Orientation)),
    \+ hascoin,
    add_path(position(X,Y)).

/* Get the position directly in front of the agent */
get_forward_position(X,Y,Z) :-
    position(OldX, OldY, Orientation),
    (
        Orientation == north -> 
            Y is OldY+1, X is OldX, Z = Orientation ;
        Orientation == east -> 
            Y is OldY, X is OldX+1, Z = Orientation ;
        Orientation == south -> 
            Y is OldY-1, X is OldX, Z = Orientation ;
        Y is OldY, X is OldX-1, Z = Orientation
    ).

/* Get the position to the left with respect to the agent */
get_left_position(X,Y,Z) :-
    position(OldX, OldY, Orientation),
    (
        Orientation == north -> 
            Y is OldY, X is OldX - 1, Z = Orientation ;
        Orientation == east -> 
            Y is OldY + 1, X is OldX, Z = Orientation ;
        Orientation == south -> 
            Y is OldY, X is OldX + 1, Z = Orientation ;
        Y is OldY - 1, X is OldX, Z = Orientation
    ).

/* Get the position to the right with respect to the agent */
get_right_position(X,Y,Z) :-
    position(OldX, OldY, Orientation),
    (
        Orientation == north -> 
            Y is OldY, X is OldX + 1, Z = Orientation ;
        Orientation == east -> 
            Y is OldY - 1, X is OldX, Z = Orientation ;
        Orientation == south -> 
            Y is OldY, X is OldX - 1, Z = Orientation ;
        Y is OldY + 1, X is OldX, Z = Orientation
    ).

/* For the senses the agent can take */

/* stench(X, Y) returns if there is a stench at X, Y */
:- dynamic(stench/2).
/* tingle(X,Y) returns if there is a tingle at X, Y */
:- dynamic(tingle/2).

/* Returns whether the wumpus is possibly at X,Y */
:- dynamic(wumpus/2).
wumpus(X,Y) :-
    \+ visited(X,Y),
    (   
      Y1 is Y-1,stench(X,Y1) ;
      Y2 is Y+1,stench(X,Y2) ;
      X1 is X-1,stench(X1,Y) ;
      X2 is X+1,stench(X2,Y)
    ).

/* Return whether a confoundus portal is at X,Y */
:- dynamic(confoundus/2).
confoundus(X,Y) :-
    \+ visited(X,Y),
    (   
      DownY is Y-1,tingle(X,DownY);
      UpY is Y+1,tingle(X,UpY);
      LeftX is X-1,tingle(LeftX, Y);
      RightX is X+1,tingle(RightX, Y)
    ).
    
/* 
Returns whether the square X,Y is safe
A square is safe if there is no wumpus and no confoundus 
*/
safe(X, Y) :-
    \+ wumpus(X, Y),
    \+ confoundus(X, Y). 

/* Functions required for assignment */
/* Sets the position of the agent back to 0,0 */
reborn :- set_position(0, 0, north).

/* Returns whether the agent has a coin */
:- dynamic(hascoin/0).

/* Conditions to choose which direction to move */

/* Used to trace the path from the current position back to the start */
trace_path(A) :-
    path(Path),
    get_last(Path, position(TargetX, TargetY)),
    get_forward_position(Fx, Fy, _),
    TargetX == Fx, TargetY == Fy,
    pop_path(_),
    A = moveforward.

trace_path(A) :-
    path(Path),
    get_last(Path, position(TargetX, TargetY)),
    get_right_position(Rx, Ry, _),
    TargetX == Rx, TargetY == Ry,
    A = turnright.

trace_path(A) :-
    path(Path),
    get_last(Path, position(TargetX, TargetY)),
    get_left_position(Lx, Ly, _),
    TargetX == Lx, TargetY == Ly,
    A = turnleft.

/* Agent has returned to the start position */
move(A, [Confounded,_,_,_,_,_]) :-
    hascoin,
    Confounded,
    A = done.

/* Agent exceeded number of moves, and is currently in the beginning */
move(A, [Confounded,_,_,_,_,_]) :-
    Confounded,
    number_of_actions(NumberOfActions),
    max_number_of_actions(MaxNumberOfActions),
    NumberOfActions >= MaxNumberOfActions,
    A = done.

/* Agent exceeded number of moves, trace path back to beginning */
move(A, _) :-
    number_of_actions(NumberOfActions),
    max_number_of_actions(MaxNumberOfActions),
    NumberOfActions >= MaxNumberOfActions,
    trace_path(A).

/* If we have the coin, we want to follow the path back to the start */
move(A, _) :-
    hascoin,
    trace_path(A).

move(A, _) :-
    hascoin,
    trace_path(A).

move(A, _) :-
    hascoin,
    trace_path(A).

/* If the current space has a coin, we pickup the coin */
move(A, [_, _, _, Glitter, _, _]) :-
    Glitter,
    A = pickup.

/* If we bumped into a wall, we are just going to turn left and continue */
move(A, [_, _, _, _, Bump, _]) :-
    Bump,
    A = turnleft.

/* If the square infront is safe, we move forward */
move(A, _) :-
    get_forward_position(X,Y,_),
    \+ visited(X, Y), safe(X, Y), !,
	A = moveforward.

/* If the square to the right is safe, we turn right */
move(A,_) :-
    get_right_position(X,Y,_),
    \+ visited(X, Y), safe(X, Y), !,
    A = turnright.

/* If there are no more unvisited nodes, go back to one of the previous safe nodes */
move(A, _) :-
    get_forward_position(X,Y,_),
    safe(X, Y), !,
	A = moveforward.

/* By default, we turn left */
move(A,_) :-
    A = turnleft.

reposition(L) :-
    write(L).

/* Starting variables */
position(0,0,north).
visited(0, 0). 