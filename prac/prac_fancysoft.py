import tensorflow as tf
import numpy as np


x_data = [[1,2,1,1],[2,1,3,2],[3,1,3,4],[4,1,5,5]
          , [1,7,5,5],[1,2,5,6],[1,6,6,6],[1,7,7,7]]
y_data = [[0],[0],[0],[1],[1],[1],[2],[2]]
nb_classes = 3 #0~2

x = tf.placeholder(tf.float32, shape=[None, 4])
y = tf.placeholder(tf.int32, shape=[None, 1])

y_one_hot = tf.one_hot(y, nb_classes)
y_one_hot = tf.reshape(y_one_hot, [-1, nb_classes])

w = tf.Variable(tf.random_normal([4, nb_classes]), name='weight')
b = tf.Variable(tf.random_normal([nb_classes]), name='bias')

logits = tf.matmul(x, w) + b
hypothesis = tf.nn.softmax(logits)

cost_i = tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=y_one_hot)
cost = tf.reduce_mean(cost_i)
optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.05).minimize(cost)

prediction = tf.argmax(hypothesis, 1)
correct_prediction = tf.equal(prediction, tf.argmax(y_one_hot,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

sess =tf.Session()
sess.run(tf.global_variables_initializer())

for step in range(2001):
    sess.run(optimizer, feed_dict={x:x_data, y:y_data})
    if step % 200 ==0:
        loss, acc = sess.run([cost, accuracy], feed_dict={x:x_data, y:y_data})
        print("step: {:5}\tLoss: {:.3f}\tAcc: {:.2%}".format(step, loss, acc))

pred = sess.run(prediction, feed_dict={x: x_data})

y_data_np = np.array(y_data)
for p, m in zip(pred, y_data_np.flatten()):
    print("[{}] Prediction: {} True Y: {}".format(p==int(m), p, int(m)))
#all = sess.run(hypothesis, feed_dict={x:[[1,11,7,9],[1,3,4,3],[1,1,0,1]]})
#print (all, sess.run(tf.arg_max(all,1)))