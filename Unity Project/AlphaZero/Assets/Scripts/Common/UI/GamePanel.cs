using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GamePanel : MonoBehaviour {

    private Game game;

    private void Start()
    {
        game = FindObjectOfType<Game>();
    }

    public void Hint()
    {
        game.Hint();
    }

    public void PauseGame()
    {
        game.PauseGame();
    }

    public void ResumeGame()
    {
        game.ResumeGame();
    }

    public void LeaveGame()
    {
        game.EndGame();
    }
}
