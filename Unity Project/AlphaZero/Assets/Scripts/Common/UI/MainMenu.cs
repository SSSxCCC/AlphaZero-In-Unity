using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class MainMenu : MonoBehaviour
{
    public void Gobang8x8()
    {
        SceneManager.LoadScene("Gobang8x8");
    }

    public void Gobang10x10()
    {
        SceneManager.LoadScene("Gobang10x10");
    }

    public void Connect4()
    {
        SceneManager.LoadScene("connect4");
    }

    public void Reversi()
    {
        SceneManager.LoadScene("Reversi8x8");
    }
}
