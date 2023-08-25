# Copyright © Microsoft Corporation.
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

from enum import Enum
import os

class RoleType(Enum):
    DEFAULT = "default"
    DEBATER = "debater"
    HOST = "host"
    TOPIC = "topic"


class ModelType(Enum):
    GPT_3_5_TURBO = os.getenv("OPENAI_API_GPT_3_5_TURBO") if os.getenv("OPENAI_API_GPT_3_5_TURBO") else "gpt-35-turbo"
    GPT_4 = os.getenv("OPENAI_API_GPT_4") if os.getenv("OPENAI_API_GPT_4") else "gpt-4"
    GPT_4_32k = "gpt-4-32k"


class TopicType(Enum):
    CAREER_EDUCATION = "Career and Education"
    PERSONAL_RELATIONSHIPS = "Personal Relationships"
    LIFESTYLE_HEALTH = "Lifestyle and Health"
    ETHICAL_MORAL_DILEMMAS = "Ethical and Moral Dilemmas"
    FINANCIAL_DECISIONS = "Financial Decisions"
    OTHER = "Other"


__all__ = ['RoleType', 'ModelType', 'TopicType']
