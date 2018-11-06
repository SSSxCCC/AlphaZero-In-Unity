using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Connect4Game : Game
{
    public Connect4Action[] actions; // 所有动作
    public Connect4Piece[] pieces; // 所有棋子
    private Connect4PieceType thisTurn;
    private Connect4PieceType playerPieceType { get { return playerFirst ? Connect4PieceType.Yellow : Connect4PieceType.Red; } }

    private int width = 7;
    private int height = 6;
    private Connect4PolicyValueNet policyValueNet;
    private MCTSPlayer mctsPlayer;
    private Connect4Board board;
    private bool aiMoved;

    public override string PlayerFirstWin { get { return "Connect4PlayerFirstWin"; } }
    public override string PlayerFirstLose { get { return "Connect4PlayerFirstLose"; } }
    public override string PlayerFirstTie { get { return "Connect4PlayerFirstTie"; } }
    public override string AiFirstWin { get { return "Connect4AIFirstWin"; } }
    public override string AiFirstLose { get { return "Connect4AIFirstLose"; } }
    public override string AiFirstTie { get { return "Connect4AIFirstTie"; } }
    public override string VersionKey { get { return "Connect4Version"; } }

    protected override void Start()
    {
        base.Start();

        for (int i = 0; i < actions.Length; i++)
        {
            actions[i].action = i;
        }

        policyValueNet = new Connect4PolicyValueNet();
        mctsPlayer = new MCTSPlayer(policyValueNet);
        board = new Connect4Board();
    }

    public override void StartGame()
    {
        board.InitBoard();
        mctsPlayer.SetPlayerInd(Connect4Board.players[playerFirst ? 1 : 0]);
        mctsPlayer.ResetPlayer();

        UpdateBoard();
        thisTurn = Connect4PieceType.Yellow;
        aiMoved = false;

        StartCoroutine("StartGameLater");
    }
    private IEnumerator StartGameLater()
    {
        yield return null;
        gameRunning = true;
    }

    private void UpdateBoard()
    {
        for (int i = 0; i < pieces.Length; i++)
        {
            if (board.states.ContainsKey(i))
            {
                Connect4PieceType pieceType = board.states[i] == Connect4Board.players[0] ? Connect4PieceType.Yellow : Connect4PieceType.Red;
                pieces[i].SetPiece(pieceType);
            }
            else
            {
                pieces[i].SetPiece(Connect4PieceType.White);
            }
        }
    }

    // 玩家或电脑输入
    private void Update()
    {
        if (!gameRunning) return;

        if (thisTurn == playerPieceType) // 轮到玩家
        {
            if (aiMoved) // 防连续触两次
            {
                aiMoved = false;
                return;
            }

            Vector3 pointedPosition;
            if (Input.GetMouseButtonDown(0)) // 鼠标操作
            {
                pointedPosition = Input.mousePosition;
            }
            else if (Input.touchCount == 1) // 触屏操作
            {
                pointedPosition = Input.touches[0].position;
            }
            else return;

            RaycastHit2D hit2D = Physics2D.CircleCast(Camera.main.ScreenToWorldPoint(pointedPosition), 0.1f, Vector2.zero);
            if (hit2D.collider == null) return; // 没点到下棋子的位置
            Connect4Action hitPiece = hit2D.collider.GetComponent<Connect4Action>();
            if (!board.GetAvailableMoves().Contains(hitPiece.action)) return; // 点的位置不合法

            // 成功下棋
            EndThisTurn(hitPiece.action);
            hintCanvas.HideHint();
        }
        else // 轮到电脑
        {
            aiMoved = true;
            int move = mctsPlayer.GetAction(board);
            EndThisTurn(move);
        }
    }

    private void EndThisTurn(int move)
    {
        // 判断是否有胜负
        board.DoMove(move);
        UpdateBoard();
        object[] endResult = board.GameEnd();
        bool end = (bool)endResult[0];
        int winner = (int)endResult[1];
        if (end)
        {
            EndGame(winner);
            return;
        }

        // 进入下一步
        thisTurn = (thisTurn == Connect4PieceType.Yellow ? Connect4PieceType.Red : Connect4PieceType.Yellow);
    }

    private void EndGame(int winner)
    {
        string endText;
        if (winner == mctsPlayer.player)
        {
            endText = "你输了";
            if (playerFirst) PlayerPrefs.SetInt(PlayerFirstLose, PlayerPrefs.GetInt(PlayerFirstLose, 0) + 1);
            else PlayerPrefs.SetInt(AiFirstLose, PlayerPrefs.GetInt(AiFirstLose, 0) + 1);
        }
        else if (winner == -1)
        {
            endText = "平局";
            if (playerFirst) PlayerPrefs.SetInt(PlayerFirstTie, PlayerPrefs.GetInt(PlayerFirstTie, 0) + 1);
            else PlayerPrefs.SetInt(AiFirstTie, PlayerPrefs.GetInt(AiFirstTie, 0) + 1);
        }
        else
        {
            endText = "你赢了";
            if (playerFirst) PlayerPrefs.SetInt(PlayerFirstWin, PlayerPrefs.GetInt(PlayerFirstWin, 0) + 1);
            else PlayerPrefs.SetInt(AiFirstWin, PlayerPrefs.GetInt(AiFirstWin, 0) + 1);
        }

        gameRunning = false;
        gameEndText.text = endText;
        gameEndText.gameObject.SetActive(true);
        Invoke("EndGame", 2f);
    }

    public override void Hint()
    {
        if (hintCanvas.showing)
            hintCanvas.HideHint();
        else
            hintCanvas.ShowHint(thisTurn == playerPieceType ? policyValueNet.PolicyValueFn(board) : null, actionTransforms);
    }
}