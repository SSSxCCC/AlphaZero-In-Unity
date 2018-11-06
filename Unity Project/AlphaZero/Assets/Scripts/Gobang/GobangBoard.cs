using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Runtime.Serialization.Formatters.Binary;
using UnityEngine;

[Serializable]
class GobangBoard : Board
{
    public int width;
    public int n_in_row;
    public Dictionary<int, int> states = new Dictionary<int, int>();

    public static readonly int[] players = { 1, 2 };

    public int currentPlayer;
    public List<int> availables = new List<int>();
    public int lastMove;

    public GobangBoard(int width, int n_in_row)
    {
        this.width = width;
        this.n_in_row = n_in_row;
    }

    public override void InitBoard(int startPlayer = 0)
    {
        currentPlayer = players[startPlayer];
        availables.Clear();
        for (int i = 0; i < GetActionCount(); i++)
        {
            availables.Add(i);
        }
        states.Clear();
        lastMove = -1;
    }

    public Vector2Int MoveToLocation(int move)
    {
        return new Vector2Int(move / width, move % width);
    }

    public int LocationToMove(Vector2Int location)
    {
        return location.x * width + location.y;
    }

    public override object CurrentState()
    {
        float[,,,] squareState = new float[1, 4, width, width];
        foreach (KeyValuePair<int, int> keyValuePair in states)
        {
            squareState[0, keyValuePair.Value == currentPlayer ? 0 : 1, width - 1 - keyValuePair.Key / width, keyValuePair.Key % width] = 1f;
        }
        if (lastMove != -1) squareState[0, 2, width - 1 - lastMove / width, lastMove % width] = 1f;
        if (states.Count % 2 == 0)
        {
            for (int i = 0; i < width; i++)
                for (int j = 0; j < width; j++)
                    squareState[0, 3, i, j] = 1f;
        }
        return squareState;
    }

    public override void DoMove(int move)
    {
        states.Add(move, currentPlayer);
        availables.Remove(move);
        currentPlayer = currentPlayer == players[1] ? players[0] : players[1];
        lastMove = move;
    }

    public override object[] GameEnd()
    {
        int[,] state = new int[width, width];
        foreach (KeyValuePair<int, int> keyValuePair in states)
            state[keyValuePair.Key / width, keyValuePair.Key % width] = keyValuePair.Value;

        int samePlayer, sameCount;

        // 水平
        for (int i = 0; i < width; i++)
        {
            samePlayer = 0;
            sameCount = 0;
            for (int j = 0; j < width; j++)
            {
                if (state[i, j] == 0)
                {
                    samePlayer = 0;
                    sameCount = 0;
                }
                else
                {
                    if (state[i, j] == samePlayer) sameCount++;
                    else
                    {
                        sameCount = 1;
                        samePlayer = state[i, j];
                    }
                }
                if (sameCount >= n_in_row)
                    return new object[] { true, samePlayer };
            }
        }
        // 垂直
        for (int j = 0; j < width; j++)
        {
            samePlayer = 0;
            sameCount = 0;
            for (int i = 0; i < width; i++)
            {
                if (state[i, j] == 0)
                {
                    samePlayer = 0;
                    sameCount = 0;
                }
                else
                {
                    if (state[i, j] == samePlayer) sameCount++;
                    else
                    {
                        sameCount = 1;
                        samePlayer = state[i, j];
                    }
                }
                if (sameCount >= n_in_row)
                    return new object[] { true, samePlayer };
            }
        }
        // 正斜
        List<int> startX = new List<int>();
        List<int> startY = new List<int>();
        for (int i = n_in_row; i <= width; i++)
        {
            startX.Add(0);
            startY.Add(width - i);
        }
        for (int i = 1; i <= width - n_in_row; i++)
        {
            startX.Add(i);
            startY.Add(0);
        }
        for (int i = 0; i < startX.Count; i++)
        {
            samePlayer = 0;
            sameCount = 0;
            for (int x = startX[i], y = startY[i]; x < width && y < width; x++, y++)
            {
                if (state[x, y] == 0)
                {
                    samePlayer = 0;
                    sameCount = 0;
                }
                else
                {
                    if (state[x, y] == samePlayer) sameCount++;
                    else
                    {
                        sameCount = 1;
                        samePlayer = state[x, y];
                    }
                }
                if (sameCount >= n_in_row)
                    return new object[] { true, samePlayer };
            }
        }
        // 反斜
        startX.Clear();
        startY.Clear();
        for (int i = n_in_row - 1; i < width; i++)
        {
            startX.Add(0);
            startY.Add(i);
        }
        for (int i = 1; i <= width - n_in_row; i++)
        {
            startX.Add(i);
            startY.Add(width - 1);
        }
        for (int i = 0; i < startX.Count; i++)
        {
            samePlayer = 0;
            sameCount = 0;
            for (int x = startX[i], y = startY[i]; x < width && y >= 0; x++, y--)
            {
                if (state[x, y] == 0)
                {
                    samePlayer = 0;
                    sameCount = 0;
                }
                else
                {
                    if (state[x, y] == samePlayer) sameCount++;
                    else
                    {
                        sameCount = 1;
                        samePlayer = state[x, y];
                    }
                }
                if (sameCount >= n_in_row)
                    return new object[] { true, samePlayer };
            }
        }

        if (availables.Count == 0) // 平局
            return new object[] { true, -1 };
        return new object[] { false, -1 }; // 没结束
    }

    public override int GetCurrentPlayer()
    {
        return currentPlayer;
    }

    public override int GetActionCount()
    {
        return width * width;
    }

    public override List<int> GetAvailableMoves()
    {
        return availables;
    }

    public override Board DeepCopy()
    {
        using (MemoryStream ms = new MemoryStream())
        {
            BinaryFormatter formatter = new BinaryFormatter();
            formatter.Serialize(ms, this);
            ms.Position = 0;
            return (Board)formatter.Deserialize(ms);
        }
    }
}