using System.Collections;
using System.Collections.Generic;
using TensorFlow;
using UnityEngine;

public class Connect4PolicyValueNet : IPolicyValueNet
{
    public int width;
    public int height;
    public TFGraph graph;
    public TFSession session;

    public Connect4PolicyValueNet(int width=7, int height=6)
    {
        this.width = width;
        this.height = height;
        graph = new TFGraph();
        graph.Import(Resources.Load<TextAsset>("Connect4/graph").bytes);
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
        for (int i = 0; i < width * width; i++)
        {
            if (legalMoves.Contains(i))
                actionPs.Add(new ActionP(i, Mathf.Exp(action_fc[0, i])));
        }

        return new PolicyValue(actionPs, evaluation);
    }
}