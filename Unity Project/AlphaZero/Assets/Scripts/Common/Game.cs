using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public abstract class Game : MonoBehaviour {

    public string version;
    public Transform[] actionTransforms;
    [HideInInspector] public bool playerFirst = false;
    protected bool gameRunning = false;

    protected GameMenu gameMenu;
    protected Text gameEndText;
    protected HintCanvas hintCanvas;

    public abstract string PlayerFirstWin { get; }
    public abstract string PlayerFirstLose { get; }
    public abstract string PlayerFirstTie { get; }
    public abstract string AiFirstWin { get; }
    public abstract string AiFirstLose { get; }
    public abstract string AiFirstTie { get; }
    public abstract string VersionKey { get; }

    protected virtual void Start()
    {
        gameMenu = FindObjectOfType<GameMenu>();
        gameEndText = GameObject.FindGameObjectWithTag("Finish").GetComponent<Text>();
        gameEndText.gameObject.SetActive(false);
        hintCanvas = FindObjectOfType<HintCanvas>();
        hintCanvas.HideHint();

        if (PlayerPrefs.GetString(VersionKey, "") != version)
        {
            PlayerPrefs.SetInt(PlayerFirstWin, 0);
            PlayerPrefs.SetInt(PlayerFirstLose, 0);
            PlayerPrefs.SetInt(PlayerFirstTie, 0);
            PlayerPrefs.SetInt(AiFirstWin, 0);
            PlayerPrefs.SetInt(AiFirstLose, 0);
            PlayerPrefs.SetInt(AiFirstTie, 0);
            PlayerPrefs.SetString(VersionKey, version);
        }
    }

    public abstract void StartGame();

    public void PauseGame()
    {
        gameRunning = false;
    }

    public void ResumeGame()
    {
        StartCoroutine("ResumeGameLater");
    }
    private IEnumerator ResumeGameLater()
    {
        yield return null;
        gameRunning = true;
    }

    public void EndGame()
    {
        gameRunning = false;
        gameEndText.gameObject.SetActive(false);
        gameMenu.gameObject.SetActive(true);
        hintCanvas.HideHint();
    }

    public abstract void Hint();
}
