using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public struct ActionP
{
    public int action;
    public float P;

    public ActionP(int action, float P)
    {
        this.action = action;
        this.P = P;
    }

    public override string ToString()
    {
        return "(" + action + ", " + P + ")";
    }
}

public class PolicyValue
{
    public List<ActionP> actionPs;
    public float V;

    public PolicyValue(List<ActionP> actionPs, float V)
    {
        this.actionPs = actionPs;
        this.V = V;
    }

    public override string ToString()
    {
        string s = "V=" + V + ", actionPs=[";
        foreach (ActionP actionP in actionPs)
        {
            s += actionP;
        }
        s += "]";
        return s;
    }
}

public interface IPolicyValueNet
{
    PolicyValue PolicyValueFn(Board board);
}