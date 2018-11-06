using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Piece : MonoBehaviour
{
    [HideInInspector] public int index; // 由Game初始化
    private SpriteRenderer spriteRenderer;

    private void Start()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
    }

    public void SetPiece(PieceType type)
    {
        switch (type)
        {
            case PieceType.Empty:
                spriteRenderer.color = Color.clear;
                break;
            case PieceType.Black:
                spriteRenderer.color = Color.black;
                break;
            case PieceType.White:
                spriteRenderer.color = Color.white;
                break;
        }
    }
}

public enum PieceType { Empty, Black, White }