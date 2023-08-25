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

from dataclasses import dataclass
from wada.typing import TopicType


@dataclass
class Topic:
    r"""The topic of the debate.

    Args:
        content (str): Original topic.
        pro (str): The proposition of the topic.
            (default: :obj:`""`)
        con (str): The contradiction of the topic.
            (default: :obj:`""`)
        background (str): The background of the topic.
            (default: :obj:`""`)
        preference (str): The preference of the subject.
            (default: :obj:`""`)
        specified_aspects (str): The specified aspects of the topic.
            (default: :obj:`""`)
        abbrev (str): The abbreviation of the topic.
            (default: :obj:`""`)
        catagory (TopicType): The catagory of the topic.
            (default: :obj:`TopicType.OTHER`)
    """
    content: str
    pro: str = ""
    con: str = ""
    background: str = ""
    preference: str = ""
    specified_aspects: str = ""
    abbr: str = ""
    catagory: TopicType = TopicType.OTHER
