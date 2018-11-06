using System.Collections;
using System.Collections.Generic;
using System.IO;
using TensorFlow;
using UnityEngine;

public class TFTest : MonoBehaviour {

	// Use this for initialization
	void Start () {
        float[] floats = new float[5];
        foreach (float f in floats)
            print(f);

		using (var graph = new TFGraph())
        {
            graph.Import(Resources.Load<TextAsset>("Gobang/graph_8_8_5").bytes);
            var session = new TFSession(graph);
            var runner = session.GetRunner();
            float[,,,] planes = new float[1, 4, 8, 8];
            planes[0, 0, 4, 4] = 1f;
            planes[0, 0, 5, 4] = 1f;
            planes[0, 0, 6, 4] = 1f;
            runner.AddInput(graph["input_states"][0], planes);
            runner.Fetch(graph["action_fc/LogSoftmax"][0], graph["evaluation_fc2/Tanh"][0]);
            var output = runner.Run();
            print("evaluation = " + ((float[,])(output[1].GetValue()))[0, 0]);
            float[,] action_fc = ((float[,])(output[0].GetValue()));
            print("action_fc:");
            for (int i = 0; i < 8; i++)
            {
                string s = "";
                for (int j = 0; j < 8; j++)
                {
                    s += Mathf.Exp(action_fc[0, i * 8 + j]) + " ";
                }
                print(s);
            }
        }
	}
	
}
