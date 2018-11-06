using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class GameMenu : MonoBehaviour
{
    public const string PlayerFirstText = "玩家先手";
    public const string AIFirstText = "玩家后手";

    public Text settingButtonText;

    private Game game;

    private void Start()
    {
        game = FindObjectOfType<Game>();
        UpdateUiBySetting();
    }

    public void Setting()
    {
        game.playerFirst = !game.playerFirst;
        UpdateUiBySetting();
    }

    public void StartGame()
    {
        game.StartGame();
        gameObject.SetActive(false);
    }

    public void MainMenu()
    {
        SceneManager.LoadScene("Main Menu");
    }

    private void UpdateUiBySetting()
    {
        if (game.playerFirst) settingButtonText.text = PlayerFirstText;
        else settingButtonText.text = AIFirstText;
    }
}