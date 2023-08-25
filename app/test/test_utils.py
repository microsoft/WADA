# Copyright © Microsoft Corporation.
# Copyright 2023 @ CAMEL-AI.org. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Modifications:
# - Added test_save_markdown_file test

from unittest import TestCase

from app.utils import save_markdown_file, split_markdown_code
from wada.messages import UserChatMessage
from wada.typing import RoleType


class TestTextUtils(TestCase):

    def test_save_markdown_file(self):
        history = [
            UserChatMessage(
                role_name='AI Debater A', role_type=RoleType.DEBATER, content=
                'I think Beijing is better than Chengdu.\n\n    I think Beijing is better than Chengdu.'
            ),
            UserChatMessage(role_name='AI Debater B',
                            role_type=RoleType.DEBATER,
                            content='I think Chengdu is better than Beijing.')
        ]

        result = {
            'model':
            'GPT 4',
            'topic':
            'This is topic',
            'topic_pro':
            'This is topic pro side',
            'topic_con':
            'This is topic con side',
            'catagory':
            'Career and Education',
            'background':
            "Beijing, as the capital city and a major hub for technology and business, offers numerous job opportunities, especially in sectors such as technology, finance, and government. The city has a thriving expatriate community and a fast-paced lifestyle, but the cost of living is relatively high, with increased expenses for housing, transportation, and food. The city suffers from air pollution, but the scale of the problem has been improving in recent years. It offers various social and cultural experiences, including historic sites, museums, and a vivid art scene. "
            "Chengdu, known for its relaxed pace of life and lower living costs compared to Beijing, may provide a more comfortable living experience. While job opportunities may not be as abundant as in Beijing, the city has been growing as a business and technology center in recent years, especially with the development of the Chengdu High-Tech Zone. The city has a more favorable climate, a greener environment, and a rich history. Chengdu is renowned for its food scene and proximity to famous tourist attractions such as the Giant Panda breeding centers and the Leshan Giant Buddha.",
            'preference':
            "Based on the provided preferences, the person places a high importance on job opportunities, he/she is willing to spend more for a vibrant city life, and prefers milder temperatures. Environmental quality and social and cultural opportunities are not important aspects in his/her decision-making process.",
            'debate_history':
            history,
            'judgement':
            "Based on the person's personal preferences, I believe that AI Debater B's argument is more convincing. The person has stated that he/she places a high importance on job opportunities, but also values a comfortable living experience and a more favorable climate. While Beijing may offer more job opportunities, Chengdu provides a more comfortable living experience with a more favorable climate and a lower cost of living. Additionally, living in a city with better air quality can contribute to a healthier living experience, which can have a positive impact on the person's overall well-being. Therefore, living in Chengdu aligns better with the person's personal preferences.",
        }

        save_markdown_file(result)

    def test_split_markdown_code_newline(self):
        inp = ("Solution: To preprocess the historical stock data, we "
               "can perform the following steps:\n\n1. Remove any unnecessary"
               " columns that do not contribute to the prediction, such as"
               " the stock symbol or date.\n2. Check for and handle any "
               "missing or null values in the data.\n3. Normalize the data"
               " to ensure that all features are on the same scale. This "
               "can be done using techniques such as Min-Max scaling or "
               "Z-score normalization.\n4. Split the data into training "
               "and testing sets. The training set will be used to train "
               "the machine learning model, while the testing set will be "
               "used to evaluate its performance.\n\nHere is an example "
               "code snippet to preprocess the data using Pandas:\n\n```\n"
               "import pandas as pd\nfrom sklearn.preprocessing import "
               "MinMaxScaler\nfrom sklearn.model_selection import "
               "train_test_split\n\n# Read in the historical stock data\ndata"
               " = pd.read_csv('historical_stock_data.csv')\n\n# Remove "
               "unnecessary columns\ndata = data.drop(['symbol', 'date'], "
               "axis=1)\n\n# Handle missing values\ndata = data.fillna("
               "method='ffill')\n\n# Normalize the data\nscaler = "
               "MinMaxScaler()\ndata = scaler.fit_transform(data)\n\n# "
               "Split the data into training and testing sets\nX_train, "
               "X_test, y_train, y_test = train_test_split(data[:, :-1], "
               "data[:, -1], test_size=0.2, random_state=42)\n```\n\nNext "
               "request.")
        gt = ("Solution: To preprocess the historical stock data, we "
              "can perform the following steps:\n\n1. Remove any unnecessary"
              " columns that do not contribute to the prediction, such as"
              " the stock symbol or date.\n2. Check for and handle any missing"
              " or null values in the data.\n3. Normalize the data to ensure"
              " that all features are on the same scale. This can be done"
              " using techniques such as Min-Max scaling or Z-score"
              " normalization.\n4. Split the data into training and testing"
              " sets. The training set will be used to train the machine"
              " learning model, while the testing set will be used to"
              " evaluate its performance.\n\nHere is an example code snippet"
              " to preprocess the data using Pandas:\n\n\n```import pandas"
              " as pd```\n```from sklearn.preprocessing import MinMaxScaler"
              "```\n```from sklearn.model_selection import train_test_split"
              "```\n\n```# Read in the historical stock data```\n```data ="
              " pd.read_csv('historical_stock_data.csv')```\n\n```# Remove"
              " unnecessary columns```\n```data = data.drop(['symbol', "
              "'date'], axis=1)```\n\n```# Handle missing values```\n```data"
              " = data.fillna(method='ffill')```\n\n```# Normalize the data"
              "```\n```scaler = MinMaxScaler()```\n```data = scaler."
              "fit_transform(data)```\n\n```# Split the data into training"
              " and testing sets```\n```X_train, X_test, y_train, y_test"
              " = train_test_split(data[:, :-1], data[:, -1], test_size=0.2,"
              " random_state=42)```\n\n\nNext request.")

        out = split_markdown_code(inp)
        self.assertEqual(out, gt)

    def test_split_markdown_code_br(self):
        inp = ("Solution: Define the Bayesian optimization object."
               "\n"
               "We can define the Bayesian optimization object using"
               " the BayesianOptimization class from the bayes_opt module."
               " Here is an example of how to define the Bayesian"
               " optimization object:"
               "\n"
               "```<br># Replace 'objective_function' with the actual"
               " objective function<br># Replace 'bounds' with the actual"
               " search space<br># Replace 'model' with the actual machine"
               " learning model<br>bo = BayesianOptimization(<br> "
               "f=objective_function,<br> pbounds=bounds,<br> verbose=2,<br>"
               " random_state=1,<br>)<br>```"
               "\n"
               "This will define the Bayesian optimization object with the"
               " specified objective function, search space, and machine"
               " learning model. The BayesianOptimization class takes "
               "several arguments, including f for the objective function,"
               " pbounds for the search space, verbose for the verbosity"
               " level, and random_state for the random seed."
               "\n"
               "Next request.")
        gt = ("Solution: Define the Bayesian optimization object."
              "\n"
              "We can define the Bayesian optimization object using the"
              " BayesianOptimization class from the bayes_opt module. Here is"
              " an example of how to define the Bayesian optimization object:"
              "\n"
              "\n```# Replace 'objective_function' with the actual objective"
              " function```\n```# Replace 'bounds' with the actual search"
              " space```\n```# Replace 'model' with the actual machine"
              " learning model```\n```bo = BayesianOptimization(```\n```"
              " f=objective_function,```\n``` pbounds=bounds,```\n``` "
              "verbose=2,```\n``` random_state=1,```\n```)```\n"
              "\n"
              "This will define the Bayesian optimization object with "
              "the specified objective function, search space, and machine"
              " learning model. The BayesianOptimization class takes several"
              " arguments, including f for the objective function, pbounds"
              " for the search space, verbose for the verbosity level, and"
              " random_state for the random seed."
              "\n"
              "Next request.")

        out = split_markdown_code(inp)
        self.assertEqual(out, gt)
