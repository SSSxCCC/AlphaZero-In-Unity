import tensorflow as tf

if __name__ == "__main__":
    with tf.Session() as sess:

        game_dir = "Gobang"
        model_dir = "model2_10_10_5"
        batch = "11000"

        # 初始化变量
        sess.run(tf.global_variables_initializer())

        # 获取最新的checkpoint，其实就是解析了checkpoint文件
        latest_ckpt = tf.train.latest_checkpoint("../" + game_dir + "/" + model_dir + "/" + batch)

        # 加载图
        restore_saver = tf.train.import_meta_graph("../" + game_dir + "/" + model_dir + "/" + batch + "/policy_value_net.model.meta")

        # 恢复图，即将weights等参数加入图对应位置中
        restore_saver.restore(sess, latest_ckpt)

        # 将图中的变量转为常量
        output_graph_def = tf.graph_util.convert_variables_to_constants(
            sess, sess.graph_def, ["action_fc/LogSoftmax", "evaluation_fc2/Tanh"])
        # 将新的图保存到"/pretrained/graph.bytes"文件中
        tf.train.write_graph(output_graph_def, "../" + game_dir + "/" + model_dir + "/" + batch, "graph.bytes", as_text=False)