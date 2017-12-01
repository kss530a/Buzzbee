def getHyparam(word):
    rnn_layer_size = 3
    seq_length = 10  # 타임시리즈 1회 처리 수
    data_dim = 2000  # 단어 수
    hidden_dim = 10  # RNNCell의 출력 넓이
    Normarization = None  # 입력데이터 일반화 - 미필요
    fc_hidden_dim = 10  # FC 내부에서 사용되는 넓이
    output_dim = 1  # 최종 출력값
    learning_rate = 0.01  # 1회 학습에서 배우는 정도
    iterations = 500  # 학습량
    #initializer = tf.contrib.layers.xavier_initializer()  # 가중치 초기값 설정
    CHECK_POINT_DIR = TB_SUMMARY_DIR = './save/LSTM'  # saver
    limitTimePoint = 70
    decideY = 0.2
    non_word_num = 2
    train_portion = 0.7

    if word == "rnn_layer_size":
        return rnn_layer_size
    elif word == "train_portion":
        return train_portion
    elif word == "seq_length":
        return seq_length
    elif word == "data_dim":
        return data_dim
    elif word == "hidden_dim":
        return hidden_dim
    elif word == "Normarization":
        return Normarization
    elif word == "fc_hidden_dim":
        return fc_hidden_dim
    elif word == "output_dim":
        return output_dim
    elif word == "learning_rate":
        return learning_rate
    elif word == "iterations":
        return iterations
    #elif word == "initializer":
    #    return initializer
    elif word == "CHECK_POINT_DIR":
        return CHECK_POINT_DIR
    elif word == "limitTimePoint":
        return limitTimePoint
    elif word == "decideY":
        return decideY
    elif word == "non_word_num":
        return non_word_num




