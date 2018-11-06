using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Runtime.Serialization.Formatters.Binary;
using UnityEngine;

[Serializable]
public class ReversiBoard : Board {

    public int width;
    public Dictionary<int, int> states = new Dictionary<int, int>();
    public static readonly int[] players = new int[] { 1, 2 };
    public int currentPlayer;
    public int lastMove;

    public ReversiBoard(int width = 8)
    {
        this.width = width;
    }

    public override void InitBoard(int start_player = 0)
    {
        currentPlayer = players[start_player];
        int opponent = currentPlayer == players[0] ? players[1] : players[0];
        int middle = width / 2;
        states.Clear();
        states.Add(locationToMove(new Vector2Int(middle - 1, middle - 1)), currentPlayer);
        states.Add(locationToMove(new Vector2Int(middle, middle)), currentPlayer);
        states.Add(locationToMove(new Vector2Int(middle - 1, middle)), opponent);
        states.Add(locationToMove(new Vector2Int(middle, middle - 1)), opponent);
        lastMove = -1;
    }

    private Vector2Int moveToLocation(int move)
    {
        return new Vector2Int(move / width, move % width);
    }

    private int locationToMove(Vector2Int location)
    {
        return location.x * width + location.y;
    }

    public override object CurrentState()
    {
        float[,,,] squareState = new float[1, 3, width, width];
        foreach (KeyValuePair<int, int> keyValuePair in states)
        {
            squareState[0, keyValuePair.Value == currentPlayer ? 0 : 1, width - 1 - keyValuePair.Key / width, keyValuePair.Key % width] = 1f;
        }
        if (states.Count % 2 == 0)
        {
            for (int i = 0; i < width; i++)
                for (int j = 0; j < width; j++)
                    squareState[0, 2, i, j] = 1f;
        }
        return squareState;
    }

    private void find(int player, List<Vector2Int> scope, List<int> allOpponentMoves)
    {
        bool findSelf = false;
        List<int> opponentMoves = new List<int>();
        foreach (Vector2Int vector2Int in scope)
        {
            int move = locationToMove(new Vector2Int(vector2Int.y, vector2Int.x));
            if (states.ContainsKey(move))
            {
                if (states[move] == player)
                {
                    findSelf = true;
                    break;
                }
                else opponentMoves.Add(move);
            }
            else break;
        }
        if (findSelf && opponentMoves.Count > 0)
            allOpponentMoves.AddRange(opponentMoves);
    }

    private bool search(int player , int h, int w, bool reverse = false)
    {
        List<int> allOpponentMoves = new List<int>();

        List<Vector2Int> scope = new List<Vector2Int>();
        for (int i = h + 1; i < width; i++) scope.Add(new Vector2Int(w, i));
        find(player, scope, allOpponentMoves);

        scope.Clear();
        for (int i = h - 1; i >= 0; i--) scope.Add(new Vector2Int(w, i));
        find(player, scope, allOpponentMoves);

        scope.Clear();
        for (int i = w - 1; i >= 0; i--) scope.Add(new Vector2Int(i, h));
        find(player, scope, allOpponentMoves);

        scope.Clear();
        for (int i = w + 1; i < width; i++) scope.Add(new Vector2Int(i, h));
        find(player, scope, allOpponentMoves);

        scope.Clear();
        for (int i = w - 1, j = h + 1; i >= 0 && j < width; i--, j++) scope.Add(new Vector2Int(i, j));
        find(player, scope, allOpponentMoves);

        scope.Clear();
        for (int i = w + 1, j = h + 1; i < width && j < width; i++, j++) scope.Add(new Vector2Int(i, j));
        find(player, scope, allOpponentMoves);

        scope.Clear();
        for (int i = w - 1, j = h - 1; i >= 0 && j > 0; i--, j--) scope.Add(new Vector2Int(i, j));
        find(player, scope, allOpponentMoves);

        scope.Clear();
        for (int i = w + 1, j = h - 1; i < width && j >= 0; i++, j--) scope.Add(new Vector2Int(i, j));
        find(player, scope, allOpponentMoves);

        if (allOpponentMoves.Count == 0)
            return false;
        if (reverse)
            foreach (int move in allOpponentMoves)
                states[move] = player;
        return true;
    }

    public override void DoMove(int move)
    {
        if (move != width * width)
        {
            states.Add(move, currentPlayer);
            Vector2Int loc = moveToLocation(move);
            search(currentPlayer, loc.x, loc.y, true);
        }
        currentPlayer = currentPlayer == players[1] ? players[0] : players[1];
        lastMove = move;
    }

    public override object[] GameEnd()
    {
        List<int> player1Availables = GetAvailableMoves(players[0]);
        List<int> player2Availables = GetAvailableMoves(players[1]);
        if (player1Availables.Count == 1 && player2Availables.Count == 1 && player1Availables[0] == width * width && player2Availables[0] == width * width)
        {
            int player1Count = 0;
            int player2Count = 0;
            foreach (KeyValuePair<int, int> keyValuePair in states)
            {
                if (keyValuePair.Value == players[0]) player1Count++;
                else if (keyValuePair.Value == players[1]) player2Count++;
                else Debug.Log("严重错误：棋盘上存在非任何玩家棋子：" + keyValuePair.Value);
            }
            if (player1Count > player2Count) return new object[] { true, players[0] };
            else if (player1Count < player2Count) return new object[] { true, players[1] };
            else return new object[] { true, -1 };
        }
        else return new object[] { false, -1 };
    }

    public override int GetCurrentPlayer()
    {
        return currentPlayer;
    }

    public override int GetActionCount()
    {
        return width * width + 1;
    }
    
    private List<int> GetAvailableMoves(int player)
    {
        List<int> availables = new List<int>();
        for (int h = 0; h < width; h++)
            for (int w = 0; w < width; w++)
            {
                int move = locationToMove(new Vector2Int(h, w));
                if (!states.ContainsKey(move) && search(player, h, w))
                    availables.Add(move);
            }
        if (availables.Count == 0)
            availables.Add(width * width);
        return availables;
    }

    public override List<int> GetAvailableMoves()
    {
        return GetAvailableMoves(currentPlayer);
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
