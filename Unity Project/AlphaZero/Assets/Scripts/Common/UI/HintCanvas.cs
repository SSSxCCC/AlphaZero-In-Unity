using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class HintCanvas : MonoBehaviour
{
    public GameObject actionPolicyTextPrefab;
    public Text valueText;

    [HideInInspector] public bool showing = false;

    private Dictionary<int, GameObject> actionTextDictionary = new Dictionary<int, GameObject>();

    public void ShowHint(PolicyValue policyValue, Transform[] actionTransforms)
    {
        HideHint();

        if (policyValue == null) return;

        valueText.text = "局面评估\n" + policyValue.V;
        valueText.gameObject.SetActive(true);
        float maxP = 0.01f;
        foreach (ActionP actionP in policyValue.actionPs)
            if (actionP.P > maxP)
                maxP = actionP.P;
        maxP = maxP * 4f / 3f;
        foreach (ActionP actionP in policyValue.actionPs)
        {
            //if (actionP.P < 0.01) continue;
            if (!actionTextDictionary.ContainsKey(actionP.action))
            {
                GameObject actionPolicyText = Instantiate(actionPolicyTextPrefab, transform);
                actionTextDictionary.Add(actionP.action, actionPolicyText);
            }
            Text actionText = actionTextDictionary[actionP.action].GetComponent<Text>();
            actionText.text = (actionP.P * 100f).ToString("F2") + "%";
            actionText.color = new Color(1, 0, 0, 0.25f + actionP.P / maxP);
            actionTextDictionary[actionP.action].transform.position = Camera.main.WorldToScreenPoint(actionTransforms[actionP.action].position);
            actionTextDictionary[actionP.action].SetActive(true);
        }
        showing = true;
    }

    public void HideHint()
    {
        valueText.gameObject.SetActive(false);
        foreach (KeyValuePair<int, GameObject> keyValuePair in actionTextDictionary)
        {
            keyValuePair.Value.SetActive(false);
        }
        showing = false;
    }
}
