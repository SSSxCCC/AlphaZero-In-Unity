using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Connect4Piece : MonoBehaviour
{
    private SpriteRenderer spriteRenderer;

    private void Start()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
    }

    public void SetPiece(Connect4PieceType type)
    {
        switch (type)
        {
            case Connect4PieceType.White:
                spriteRenderer.color = Color.white;
                break;
            case Connect4PieceType.Yellow:
                spriteRenderer.color = Color.yellow;
                break;
            case Connect4PieceType.Red:
                spriteRenderer.color = Color.red;
                break;
        }
    }
}

public enum Connect4PieceType { White, Yellow, Red }