using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TreeNode
{
    public TreeNode parent;
    public Dictionary<int, TreeNode> children = new Dictionary<int, TreeNode>();
    public int n_visits = 0;
    public float Q = 0f;
    public float P;

    public TreeNode(TreeNode parent, float P)
    {
        this.parent = parent;
        this.P = P;
    }

    public void Expand(List<ActionP> action_priors)
    {
        foreach (ActionP action_prior in action_priors)
        {
            if (!children.ContainsKey(action_prior.action))
            {
                children.Add(action_prior.action, new TreeNode(this, action_prior.P));
            }
        }
    }

    public object[] Select(float c_puct)
    {
        int action = -1;
        TreeNode node = null;
        float maxValue = float.MinValue;
        foreach (KeyValuePair<int, TreeNode> keyValuePair in children)
        {
            float value = keyValuePair.Value.GetValue(c_puct);
            if (value > maxValue)
            {
                action = keyValuePair.Key;
                node = keyValuePair.Value;
                maxValue = value;
            }
        }
        return new object[] { action, node };
    }

    public void Update(float leaf_value)
    {
        n_visits++;
        Q += (leaf_value - Q) / n_visits;
    }

    public void UpdateRecursive(float leafValue)
    {
        if (parent != null)
            parent.UpdateRecursive(-leafValue);
        Update(leafValue);
    }

    public float GetValue(float c_puct)
    {
        float u = c_puct * P * Mathf.Sqrt(parent.n_visits) / (1 + n_visits);
        return Q + u;
    }

    public bool IsLeaf()
    {
        return children.Count == 0;
    }

    public bool IsRoot()
    {
        return parent == null;
    }
}

public class MCTS
{
    public TreeNode root;
    public IPolicyValueNet policy;
    public float c_puct;
    public int n_playout;

    public MCTS(IPolicyValueNet policyValueNet, float c_puct = 5f, int n_playout = 300)
    {
        root = new TreeNode(null, 1f);
        policy = policyValueNet;
        this.c_puct = c_puct;
        this.n_playout = n_playout;
    }

    public void Playout(Board state)
    {
        TreeNode node = root;
        while (!node.IsLeaf())
        {
            object[] selectResult = node.Select(c_puct);
            node = (TreeNode)selectResult[1];
            state.DoMove((int)selectResult[0]);
        }
        PolicyValue policyValue = policy.PolicyValueFn(state);
        float leafValue = policyValue.V;
        object[] var = state.GameEnd();
        bool end = (bool)var[0];
        int winner = (int)var[1];
        if (!end)
            node.Expand(policyValue.actionPs);
        else
        {
            if (winner == -1)
                leafValue = 0;
            else
                leafValue = (winner == state.GetCurrentPlayer() ? 1f : -1f);
        }
        node.UpdateRecursive(-leafValue);
    }

    public List<ActionP> GetMoveProbs(Board state, float temp = 1e-3f)
    {
        for (int i = 0; i < n_playout; i++)
        {
            Board stateCopy = state.DeepCopy();
            Playout(stateCopy);
        }

        List<int> acts = new List<int>();
        List<float> actP = new List<float>();
        foreach (KeyValuePair<int, TreeNode> keyValuePair in root.children)
        {
            acts.Add(keyValuePair.Key);
            actP.Add(1f / temp * Mathf.Log(keyValuePair.Value.n_visits + 1e-10f));
        }
        actP = softmax(actP);

        List<ActionP> actionPs = new List<ActionP>();
        for (int i = 0; i < acts.Count; i++)
        {
            actionPs.Add(new ActionP(acts[i], actP[i]));
        }
        return actionPs;
    }

    public void UpdateWithMove(int lastMove)
    {
        if (root.children.ContainsKey(lastMove))
        {
            root = root.children[lastMove];
            root.parent = null;
        }
        else
        {
            root = new TreeNode(null, 1f);
        }
    }

    private List<float> softmax(List<float> xList)
    {
        float xMax = Mathf.Max(xList.ToArray());
        float xSum = 0f;
        for (int i = 0; i < xList.Count; i++)
        {
            xList[i] = Mathf.Exp(xList[i] - xMax);
            xSum += xList[i];
        }
        for (int i = 0; i < xList.Count; i++)
        {
            xList[i] /= xSum;
        }
        return xList;
    }
}

class MCTSPlayer
{
    public MCTS mcts;
    public int player;

    public MCTSPlayer(IPolicyValueNet policyValueNet, float c_puct = 5, int n_playout = 300)
    {
        mcts = new MCTS(policyValueNet, c_puct, n_playout);
    }

    public void SetPlayerInd(int p)
    {
        player = p;
    }

    public void ResetPlayer()
    {
        mcts.UpdateWithMove(-1);
    }

    public int GetAction(Board board, float temp = 1e-3f)
    {
        if (board.GetAvailableMoves().Count > 0)
        {
            List<ActionP> actsProbs = mcts.GetMoveProbs(board, temp);
            mcts.UpdateWithMove(-1);

            float sumP = 0;
            foreach (ActionP actionP in actsProbs)
            {
                sumP += actionP.P;
            }
            float random = Random.Range(0, sumP);
            float currentP = 0;
            foreach (ActionP actionP in actsProbs)
            {
                currentP += actionP.P;
                if (random <= currentP)
                    return actionP.action;
            }
            return actsProbs[actsProbs.Count - 1].action;
        }
        else
        {
            throw new System.Exception("AI没有位置可以走了！");
        }
    }
}