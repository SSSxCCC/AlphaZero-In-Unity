using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DisableObjectOnActive : MonoBehaviour {

    public GameObject objectToDisable;

    private void OnEnable()
    {
        objectToDisable.SetActive(false);
    }
}
