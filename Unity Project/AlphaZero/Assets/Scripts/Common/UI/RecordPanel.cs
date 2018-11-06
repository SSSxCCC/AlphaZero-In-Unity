using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class RecordPanel : MonoBehaviour
{
    public Text aiVersion;
    public Text playerFirstWin;
    public Text playerFirstLose;
    public Text playerFirstTie;
    public Text aiFirstWin;
    public Text aiFirstLose;
    public Text aiFirstTie;

    private Game game;

    private void Awake()
    {
        game = FindObjectOfType<Game>();
    }

    private void OnEnable()
    {
        aiVersion.text = "电脑版本：" + PlayerPrefs.GetString(game.VersionKey, "");
        playerFirstWin.text = PlayerPrefs.GetInt(game.PlayerFirstWin, 0).ToString();
        playerFirstLose.text = PlayerPrefs.GetInt(game.PlayerFirstLose, 0).ToString();
        playerFirstTie.text = PlayerPrefs.GetInt(game.PlayerFirstTie, 0).ToString();
        aiFirstWin.text = PlayerPrefs.GetInt(game.AiFirstWin, 0).ToString();
        aiFirstLose.text = PlayerPrefs.GetInt(game.AiFirstLose, 0).ToString();
        aiFirstTie.text = PlayerPrefs.GetInt(game.AiFirstTie, 0).ToString();
    }
}