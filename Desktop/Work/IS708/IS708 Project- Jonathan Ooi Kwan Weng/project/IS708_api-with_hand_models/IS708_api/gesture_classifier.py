import json
import pickle

import numpy as np
import pandas as pd
import tsfel

source_path = "segments_train"

GESTURE_MODEL_FILENAME = 'gesture_clf'


def predict(raw_segment_dataframe):
    # Sampling frequency - number of samples per second - the timeframe is 2 seconds with 50 samples
    fs = 25
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)

    # Config file with the features meant to be extracted
    with open('cfg_file.json') as f:
        cfg_file = json.load(f)

    # Scaler for data normalization
    with open('scalar.pkl', 'rb') as f:
        scaler = pickle.load(f)

    # Drops the first and last columns of the data as we do not need them for the feature extraction - Timestamp and gesture type
    # Ensure the data being fed in has these columns, else features will not be extracted properly
    raw_segment_dataframe.drop(raw_segment_dataframe.columns[len(raw_segment_dataframe.columns) - 1], axis=1,
                               inplace=True)

    raw_segment_dataframe.drop(raw_segment_dataframe.columns[0], axis=1, inplace=True)

    # If the length of the csv files are less than 50 rows, pad the empty blocks with zeros
    if len(raw_segment_dataframe) < 50:
        for i in range(len(raw_segment_dataframe), 50):
            raw_segment_dataframe.loc[i] = 0

    # If the length is greater than 50 rows, trim it to 50 rows
    else:
        raw_segment_dataframe = raw_segment_dataframe.head(50)

    # Extract features from the data fed in
    features = tsfel.time_series_features_extractor(cfg_file, raw_segment_dataframe, fs=fs, window_size=50)

    # Normalize data
    nX_test = scaler.transform(features)

    # Predict the gesture type
    test_predict = model.predict(nX_test)

    predicted_label = ''

    # Output the gesture type in string depending on the output
    if np.array_str(test_predict) == '[0]':
        predicted_label = 'Null'

    elif np.array_str(test_predict) == '[1]':
        predicted_label = 'Nodding'

    elif np.array_str(test_predict) == '[2]':
        predicted_label = 'Shaking'

    # Print for your viewing convenience
    print(predicted_label)
    return predicted_label


if __name__ == '__main__':
    # Testing with csv files - model training is below this
    df = pd.read_csv('segments_train/80_Null.csv')
    output = predict(df)
    print(output)
    df = pd.read_csv('segments_train/98_Nodding.csv')
    output1 = predict(df)
    print(output1)
    df = pd.read_csv('segments_train/99_Shaking.csv')
    output2 = predict(df)
    print(output2)
    df = pd.read_csv('segments_train/100_Nodding.csv')
    output3 = predict(df)
    print(output3)
    df = pd.read_csv('segments_train/81_Null.csv')
    output4 = predict(df)
    print(output4)
    df = pd.read_csv('segments_train/82_Null.csv')
    output5 = predict(df)
    print(output5)
    df = pd.read_csv('segments_train/146_Nodding.csv')
    output6 = predict(df)
    print(output6)
    df = pd.read_csv('segments_train/147_Shaking.csv')
    output7 = predict(df)
    print(output7)
    df = pd.read_csv('segments_train/149_Shaking.csv')
    output8 = predict(df)
    print(output8)

    ## getting all the files in source path
    # files = [f for f in listdir(source_path) if f.endswith('.csv')]
    # print(files)

    # ---------------------------------------File preprocessing --------------------------------------------#

    # File padding and cutting to make all the entries for each training file even length
    # for i in range(0, len(files)):
    #     folder = str('segments_train/' + files[i])
    #     print(folder)
    #     df = pd.read_csv(folder)
    #
    #     print(len(df))
    #     if len(df) < 50:
    #         for i in range(len(df), 50):
    #             df.loc[i] = 0
    #             # print("abs")
    #
    #     else:
    #         df = pd.read_csv(folder, nrows=50)
    #         print(df)
    #
    #       df.to_csv('output.csv', encoding='utf-8', index=False, mode='a', header=False)

    # obtaining labels from the files

    # for i in range(0, len(files)):
    #     print(type(files[i]))
    #     if 'Null' in files[i]:
    #         with open('labels.csv', 'a') as file:
    #             file.write('0')
    #             file.write("\n")
    #
    #     elif 'Nodding' in files[i]:
    #         with open('labels.csv', 'a') as file:
    #             file.write('1')
    #             file.write("\n")
    #
    #     elif 'Shaking' in files[i]:
    #         with open('labels.csv', 'a') as file:
    #             file.write('2')
    #             file.write("\n")

    # print(files[i])

    #     # print(len(files))
    #     # print(len(df))
    #     # print(df)
    #

    # -------------------------------------------------------------Feature extraction-------------------------------------------------------------
#     activity_labels = np.array(pd.read_csv('activity_labels.txt', header=None, delimiter=' '))[:, 1]
#
#     # Sampling frequency - number of samples per second - the timeframe is 2 seconds with 50 samples
#     fs = 25
#
#     with open('cfg_file.json') as f:
#         cfg_file = json.load(f)
#
#     # Reads the csv with training data
#     df = pd.read_csv('output1.csv', header=None)
#     labels = pd.read_csv('labels.csv', header=None)
#
#     features = tsfel.time_series_features_extractor(cfg_file, df, fs=fs, window_size=50)
#     print(features)
#     X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.4, random_state=10)
#
# # Convert to numpy array
#     X_train = X_train.to_numpy()
#     X_test = X_test.to_numpy()
#     y_train = y_train.to_numpy()
#     y_test = y_test.to_numpy()
#
#
# --------------------------------------Data normalization-------------------------------------
#     scaler = preprocessing.StandardScaler()
#     nX_train = scaler.fit_transform(X_train)
#
#     with open('scalar.pkl', 'wb') as f:
#         pickle.dump(scaler, f)
#     nX_test = scaler.transform(X_test)
#
# ----------------------------------Classifer training------------------------------------------
#
#     model = RandomForestClassifier()
#     model.fit(nX_train, y_train.ravel())
#
#
# ----------------------------- Using the train model to predict------------------------------------
#     y_test_predict = model.predict(nX_test)
#     accuracy = accuracy_score(y_test, y_test_predict) * 100
#     print("Accuracy: " + str(accuracy) + '%')
#     print(classification_report(y_test, y_test_predict, target_names=activity_labels))
#
# --------------------------------------------saving model------------------------------------
#     with open('model1.pkl', 'wb') as f:
#         pickle.dump(model, f)

# with open('model.pkl', 'rb') as f:
#     model = pickle.load(f)
#
# ------------------------------------------Classification matrix---------------------------------
# y_test_predict = model.predict(nX_test)
# print(y_test_predict)
# accuracy = accuracy_score(y_test, y_test_predict) * 100
# print("Accuracy: " + str(accuracy) + '%')
# print(classification_report(y_test, y_test_predict, target_names=activity_labels))
