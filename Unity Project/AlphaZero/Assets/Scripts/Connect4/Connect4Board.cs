using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Runtime.Serialization.Formatters.Binary;
using UnityEngine;

[Serializable]
public class Connect4Board : Board
{
    public int width;
    public int height;
    public int n_in_row;

    public int currentPlayer;
    public int lastMove;

    public Dictionary<int, int> states = new Dictionary<int, int>();
    public static readonly int[] players = new int[] { 1, 2 };

    public Connect4Board(int width=7, int height=6)
    {
        this.width = width;
        this.height = height;
        n_in_row = 4;
    }

    public override void InitBoard(int start_player = 0)
    {
        currentPlayer = players[start_player];
        lastMove = -1;
        states.Clear();
    }

    public override object CurrentState()
    {
        float[,,,] squareState = new float[1, 3, height, width];
        foreach (KeyValuePair<int, int> keyValuePair in states)
        {
            squareState[0, keyValuePair.Value == currentPlayer ? 0 : 1, height - 1 - keyValuePair.Key / width, keyValuePair.Key % width] = 1f;
        }
        if (states.Count % 2 == 0)
        {
            for (int i = 0; i < height; i++)
                for (int j = 0; j < width; j++)
                    squareState[0, 2, i, j] = 1f;
        }
        return squareState;
    }

    private int moveToLocation(int move)
    {
        if (move < width)
        {
            while (states.ContainsKey(move))
                move += width;
            return move;
        }
        else return -1;
    }

    public override void DoMove(int move)
    {
        if (move < width)
            states.Add(moveToLocation(move), currentPlayer);
        else
        {
            for (int loc = move - width; loc < width * height; loc += width)
            {
                if (!states.ContainsKey(loc))
                    break;
                else if (!states.ContainsKey(loc + width))
                    states.Remove(loc);
                else
                    states[loc] = states[loc + width];
            }
        }

        currentPlayer = currentPlayer == players[1] ? players[0] : players[1];
        lastMove = move;
    }

    public override object[] GameEnd()
    {
        int[,] state = new int[height, width];
        foreach (KeyValuePair<int, int> keyValuePair in states)
            state[keyValuePair.Key / width, keyValuePair.Key % width] = keyValuePair.Value;

        int samePlayer, sameCount;
        int winner = -1;
        bool hasWinner = false;

        // 水平
        for (int i = 0; i < height; i++)
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
                {
                    //return new object[] { true, samePlayer };
                    if (hasWinner && winner != samePlayer)
                        return new object[] { true, -1 };
                    else if (!hasWinner)
                    {
                        winner = samePlayer;
                        hasWinner = true;
                    }
                }
            }
        }
        // 垂直
        for (int j = 0; j < width; j++)
        {
            samePlayer = 0;
            sameCount = 0;
            for (int i = 0; i < height; i++)
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
                {
                    //return new object[] { true, samePlayer };
                    if (hasWinner && winner != samePlayer)
                        return new object[] { true, -1 };
                    else if (!hasWinner)
                    {
                        winner = samePlayer;
                        hasWinner = true;
                    }
                }
            }
        }
        // 正斜
        List<int> startX = new List<int>();
        List<int> startY = new List<int>();
        for (int i = n_in_row; i <= height; i++)
        {
            startX.Add(0);
            startY.Add(height - i);
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
            for (int x = startX[i], y = startY[i]; x < width && y < height; x++, y++)
            {
                if (state[y, x] == 0)
                {
                    samePlayer = 0;
                    sameCount = 0;
                }
                else
                {
                    if (state[y, x] == samePlayer) sameCount++;
                    else
                    {
                        sameCount = 1;
                        samePlayer = state[y, x];
                    }
                }
                if (sameCount >= n_in_row)
                {
                    //return new object[] { true, samePlayer };
                    if (hasWinner && winner != samePlayer)
                        return new object[] { true, -1 };
                    else if (!hasWinner)
                    {
                        winner = samePlayer;
                        hasWinner = true;
                    }
                }
            }
        }
        // 反斜
        startX.Clear();
        startY.Clear();
        for (int i = n_in_row - 1; i < height; i++)
        {
            startX.Add(0);
            startY.Add(i);
        }
        for (int i = 1; i <= width - n_in_row; i++)
        {
            startX.Add(i);
            startY.Add(height - 1);
        }
        for (int i = 0; i < startX.Count; i++)
        {
            samePlayer = 0;
            sameCount = 0;
            for (int x = startX[i], y = startY[i]; x < width && y >= 0; x++, y--)
            {
                if (state[y, x] == 0)
                {
                    samePlayer = 0;
                    sameCount = 0;
                }
                else
                {
                    if (state[y, x] == samePlayer) sameCount++;
                    else
                    {
                        sameCount = 1;
                        samePlayer = state[y, x];
                    }
                }
                if (sameCount >= n_in_row)
                {
                    //return new object[] { true, samePlayer };
                    if (hasWinner && winner != samePlayer)
                        return new object[] { true, -1 };
                    else if (!hasWinner)
                    {
                        winner = samePlayer;
                        hasWinner = true;
                    }
                }
            }
        }

        if (hasWinner)
            return new object[] { true, winner };
        else if (GetAvailableMoves().Count == 0) // 平局
            return new object[] { true, -1 };
        else
            return new object[] { false, -1 }; // 没结束
    }

    public override int GetCurrentPlayer()
    {
        return currentPlayer;
    }

    public override int GetActionCount()
    {
        return width * 2;
    }

    public override List<int> GetAvailableMoves()
    {
        List<int> availables = new List<int>();
        for (int move = 0; move < width; move++)
            if (!states.ContainsKey(move + width * (height - 1)))
                availables.Add(move);
        for (int move = width; move < width * 2; move++)
            if (states.ContainsKey(move - width) && states[move - width] == currentPlayer)
                availables.Add(move);
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
