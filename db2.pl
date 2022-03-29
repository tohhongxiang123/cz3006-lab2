wumpus(X,Y) :-
    \+ visited(X,Y),
    (   
      Y is Y-1,stench(X,Y);
      Y is Y+1,stench(X,Y);
      X is X-1,stench(X, Y);
      X is X+1,stench(X, Y)
    ).

confoundus(X,Y) :-
    \+ visited(X,Y),
    (   
      DownY is Y-1,tingle(X,DownY);
      UpY is Y+1,tingle(X,UpY);
      LeftX is X-1,tingle(LeftX, Y);
      RightX is X+1,tingle(RightX, Y)
    ).

new_position(X,Y,Z) :-
    position(OldX,OldY,OldZ),
    (   
    	Z == north ->  X is OldX, Y is OldY+1, Z is OldZ ;
    	Z == south ->  X is OldX, Y is OldY-1, Z is OldZ ;
        Z == east ->  X is OldX+1, Y is OldY, Z is OldZ ;
        X is OldX-1, Y is OldY, Z is OldZ
    ).

move(A) :-
    new_position(X,Y,Z).
	A = moveforward,
		\+ wumpus(X,Y),
		\+ confoundus(X,Y) ;
	A = turnleft.
    
position(0,0,north).
stench(1,1).
visited(0,1).