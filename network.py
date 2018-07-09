import tensorflow as tf


class Network(object):
    def __init__(self, depth=5, width=48):
        self.sess = tf.Session()
        # Network's depth and width.
        self.depth = depth
        self.width = width

    # Set up network structure.
    def set_up(self):
        self.global_step = tf.Variable(0, name="global_step", trainable=False)
        # Input: 15x15x5, output: 225+1.
        self.input = tf.placeholder(tf.float32, [None, 15, 15, 5])
        self.value = tf.placeholder(tf.float32, [None, 1])
        self.policy = tf.placeholder(tf.float32, [None, 226])

        # First layer.
        with tf.name_scope('Input-Layer'):
            conv = tf.layers.conv2d(
                self.input, self.width, 3, padding='same', name='conv1')
            conv = tf.layers.batch_normalization(conv, name='bn1')
            net = tf.nn.relu(conv)

        # Residual layer.
        for i in range(1, self.depth+1):
            with tf.name_scope('Res'+str(i)):
                conv = tf.layers.conv2d(net, self.width, 3, padding='same',
                                        name='conv'+str(i)+'-1')
                conv = tf.layers.batch_normalization(
                    conv, name='bn'+str(i)+'-1')
                conv = tf.nn.relu(conv)
                conv = tf.layers.conv2d(conv, self.width, 3, padding='same',
                                        name='conv'+str(i)+'-2')
                conv = tf.layers.batch_normalization(
                    conv, name='bn'+str(i)+'-2')
                net = tf.nn.relu(conv + net)

        # Policy output.
        with tf.name_scope('Policy'):
            policy = tf.layers.conv2d(net, 2, 1,
                                      padding='same', name='policy-conv')
            policy = tf.layers.batch_normalization(policy, name='policy-bn')
            policy = tf.reshape(policy, [-1, 15*15*2])
            policy = tf.layers.dense(policy, 226, tf.nn.relu)

        with tf.name_scope('Policy-Output'):
            self.policy_output = tf.nn.softmax(policy, name='output')

        # Value output.
        with tf.name_scope('Value'):
            value = tf.layers.conv2d(net, 1, 1,
                                     padding='same', name='value-conv')
            value = tf.layers.batch_normalization(value, name='value-bn')
            value = tf.reshape(value, [-1, 15*15])
            value = tf.layers.dense(value, 128, tf.nn.relu)
            value = tf.layers.batch_normalization(value, name='value-bn2')

        with tf.name_scope('Value-Output'):
            self.value_output = tf.layers.dense(value, 1, tf.nn.tanh)

        # Loss function.
        with tf.name_scope('Policy-Loss'):
            self.policy_loss = tf.reduce_mean(
                tf.nn.softmax_cross_entropy_with_logits_v2(logits=policy,
                                                           labels=self.policy))
        tf.summary.scalar('policy-loss', self.policy_loss)

        with tf.name_scope('Value-Loss'):
            self.value_loss = tf.reduce_mean(tf.losses.mean_squared_error(
                labels=self.value, predictions=self.value_output))

        tf.summary.scalar('value-loss', self.value_loss)

        # Optimizer.
        self.policy_opt = tf.train.RMSPropOptimizer(1e-3).minimize(
            self.policy_loss, global_step=self.global_step)
        self.value_opt = tf.train.RMSPropOptimizer(1e-3).minimize(
            self.value_loss, global_step=self.global_step)
        # self.opt = tf.train.AdamOptimizer(1e-4).minimize(
        #    self.loss, global_step=self.global_step)

        # Accuracy.
        with tf.name_scope('Accuracy'):
            acc = tf.equal(tf.argmax(policy, 1), tf.argmax(self.policy, 1))
            self.accuracy = tf.reduce_mean(tf.cast(acc, tf.float32))

        tf.summary.scalar('accuracy', self.accuracy)

        # Summary.
        self.merged = tf.summary.merge_all()
        self.train_writer = tf.summary.FileWriter(
            "logs/train", self.sess.graph)
        self.test_writer = tf.summary.FileWriter(
            "logs/test", self.sess.graph)

    # Initialize variable.
    def init_var(self):
        self.sess.run(tf.global_variables_initializer())

    def _get_global_step(self):
        return self.sess.run(self.global_step)

    # Train network.
    def train(self, train_data, test_data, batch_size):
        print('Training ...')
        for i in range(train_data.data_size // batch_size):
            # Upgrade accuracy to summary.
            if i % 50 == 0:
                step = self._get_global_step()
                # Accuracy of train data.
                x, y = train_data.get_random_data(512)
                summ = self.sess.run(
                    self.merged, {self.input: x, self.policy: y})
                self.train_writer.add_summary(summ, step)
                # Accuracy of test data.
                x, y = test_data.get_random_data(512)
                testSumm = self.sess.run(
                    self.merged, {self.input: x, self.policy: y})
                self.test_writer.add_summary(testSumm, step)

            # Get in/out data.
            x, y = train_data.get_data(i * batch_size, batch_size)
            # Train network.
            self.sess.run([self.opt], {self.input: x, self.policy: y})

    # Save/Load network.
    def save(self, path='net/nn'):
        tf.train.Saver().save(self.sess, path)

    def load(self, path='net/nn'):
        tf.train.Saver().restore(self.sess, path)

    def output_policy(self, input):
        prob = self.sess.run(self.policy_output, feed_dict={self.input: input})
        return prob.reshape([226])

    def output_value(self, input):
        return self.sess.run(self.value_output, feed_dict={self.input: input})[0][0]

    def display_network(self, input):
        summ = self.sess.run(self.merged, {self.input: input,
                                           self.policy: [[0]*226],
                                           self.value: [[0]]})
        self.train_writer.add_summary(summ, 0)


def main():
    net = Network()
    net.set_up()
    net.init_var()
    input = [[[[0]*5]*15]*15]
    print(input)
    print(net.output_policy(input))
    print(net.output_value(input))
    net.display_network(input)


if __name__ == '__main__':
    main()
