using System.Collections;
using System.Collections.Generic;
using TensorFlow;
using UnityEngine;

public class ReversiPolicyValueNet : IPolicyValueNet
{
    public int width;
    public TFGraph graph;
    public TFSession session;

    public ReversiPolicyValueNet(int width)
    {
        this.width = width;
        graph = new TFGraph();
        graph.Import(Resources.Load<TextAsset>("Reversi/graph").bytes);
        session = new TFSession(graph);
    }

    public PolicyValue PolicyValueFn(Board board)
    {
        HashSet<int> legalMoves = new HashSet<int>(board.GetAvailableMoves());
        float[,,,] currentState = (float[,,,])board.CurrentState();

        TFSession.Runner runner = session.GetRunner();
        runner.AddInput(graph["input_states"][0], currentState);
        runner.Fetch(graph["action_fc/LogSoftmax"][0], graph["evaluation_fc2/Tanh"][0]);
        TFTensor[] output = runner.Run();

        float evaluation = ((float[,])(output[1].GetValue()))[0, 0];

        float[,] action_fc = ((float[,])(output[0].GetValue()));
        List<ActionP> actionPs = new List<ActionP>();
        for (int i = 0; i < board.GetActionCount(); i++)
        {
            if (legalMoves.Contains(i))
                actionPs.Add(new ActionP(i, Mathf.Exp(action_fc[0, i])));
        }

        return new PolicyValue(actionPs, evaluation);
    }
}