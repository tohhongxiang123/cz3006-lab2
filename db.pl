/* position(x, y, orientation) */
:- dynamic(position/3).
position(0,0,north).

set_position(position(X, Y, Z)) :-
    call(position(OldX, OldY, OldZ)),
    retract(position(OldX, OldY, OldZ)),
    assertz(position(X, Y, Z)),
    /* When agent changes position, assert that the new position is visited */
    assertz(visited(X, Y)).

/* Whether X, Y in the grid is visited. In the beginning, (0,0) is visited */
:- dynamic(visited/2).
visited(0, 0). 

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

hasarrow.

turn_left :-
    position(X, Y, Orientation),
    (
        Orientation == north -> set_position(position(X,Y,west)) ;
        Orientation == west -> set_position(position(X,Y,south)) ;
        Orientation == south -> set_position(position(X,Y,east)) ;
        set_position(position(X,Y,north))
    ).

turn_right :-
    position(X, Y, Orientation),
    (
        Orientation == north -> set_position(position(X,Y,east)) ;
        Orientation == east -> set_position(position(X,Y,south)) ;
        Orientation == south -> set_position(position(X,Y,west)) ;
        set_position(position(X,Y,north))
    ).

move_forward :-
    position(X, Y, Orientation),
    (
        Orientation == north -> 
            NewY is Y + 1,
            NewX is X ;
        Orientation == east -> 
            NewX is X + 1,
            NewY is Y ;
        Orientation == south -> 
            NewX is X,
            NewY is Y - 1 ;
        NewX is X - 1,
        NewY is Y
    ),
    set_position(position(NewX, NewY, Orientation)).

/* Functions required for assignment */
reborn :- set_position(0, 0, north).
    
move(A, L) :-
    A = moveforward.

reposition(L) :-
    write(L).

