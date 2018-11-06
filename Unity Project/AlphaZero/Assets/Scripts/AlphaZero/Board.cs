using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public abstract class Board
{
    public abstract void InitBoard(int start_player = 0);
    public abstract object CurrentState();
    public abstract void DoMove(int move);
    public abstract object[] GameEnd();
    public abstract int GetCurrentPlayer();
    public abstract int GetActionCount();
    public abstract List<int> GetAvailableMoves();
    public abstract Board DeepCopy();
}

