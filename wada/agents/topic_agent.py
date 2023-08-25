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

import re
from typing import Any, Tuple

from colorama import Fore

from wada.agents import ChatAgent
from wada.generators import DebatePromptGenerator, SystemMessageGenerator
from wada.messages import UserChatMessage
from wada.topic import Topic
from wada.typing import ModelType, RoleType


class TopicAgent(ChatAgent):
    r"""A chat agent that can deal with a topic.

    Args:
        topic (Topic): The topic of the agent.
        model (ModelType): The model type to use for the agent.
            (default: :obj:`ModelType.GPT_4`)
        menu_color (Any): The output color in console.
            (default: :obj:`Fore.MAGENTA`)
        role_name (str): The role name of the agent.
            (default: :obj:`"Host"`)
        question_limit (int): The maximum number of questions to ask.
            (default: :obj:`10`)
    """

    def __init__(
        self,
        topic: Topic,
        model: ModelType = ModelType.GPT_4,
        menu_color: Any = Fore.CYAN,
        role_name: str = "Topic Specifier",
        question_limit: int = 10,
    ) -> None:

        system_message = SystemMessageGenerator().from_dict(
            meta_dict=None, role_tuple=(role_name, RoleType.TOPIC))

        super().__init__(system_message, model, temperature=1.0)

        self.topic = topic
        self.menu_color = menu_color
        self.role_name = role_name
        self.question_limit = question_limit

    def break_down_topic(self) -> Tuple[str, str]:
        prompt = DebatePromptGenerator().get_topic_break_down_prompt(
            self.topic.content)
        chat_msg = UserChatMessage(role_name=self.role_name,
                                   role_type=RoleType.TOPIC, content=prompt)
        print(self.topic)

        replies, terminated, info = self.step(chat_msg)
        if terminated or replies is None:
            raise ValueError(f"Breaking down topic failed due to {info}")

        pro_regex = r"PRO:\s(.+)"
        con_regex = r"CON:\s(.+)"

        self.update_messages(replies[0])
        content = replies[0].content

        pro_match = re.search(pro_regex, content)
        if pro_match:
            pro_content = pro_match.group(1)
            print("Pro statement:\n", pro_content)

        con_match = re.search(con_regex, content)
        if con_match:
            con_content = con_match.group(1)
            print("Con statement:\n", con_content)

        self.topic.pro = pro_content
        self.topic.con = con_content

        return (pro_content, con_content)

    def specify_topic(self) -> str:
        prompt = DebatePromptGenerator().get_topic_specify_prompt(
            topic=self.topic)

        chat_msg = UserChatMessage(role_name=self.role_name,
                                   role_type=RoleType.TOPIC, content=prompt)
        replies, terminated, info = self.step(chat_msg)
        if terminated or replies is None:
            raise ValueError(f"Specifying topic failed due to {info}")

        self.update_messages(replies[0])
        self.topic.specified_aspects = replies[0].content
        print(self.menu_color + self.topic.specified_aspects)
        return self.topic.specified_aspects

    def abbreviate_topic(self) -> str:
        prompt = DebatePromptGenerator().get_topic_abbreviate_prompt(
            topic=self.topic)

        chat_msg = UserChatMessage(role_name=self.role_name,
                                   role_type=RoleType.TOPIC, content=prompt)
        replies, terminated, info = self.step(chat_msg)
        if terminated or replies is None:
            raise ValueError(f"Abbreviating topic failed due to {info}")

        self.update_messages(replies[0])
        self.topic.abbr = replies[0].content
        print(self.menu_color + self.topic.abbr)
        return self.topic.abbr

    def collect_bg(self) -> str:
        prompt = DebatePromptGenerator().get_collect_bg_prompt()
        chat_msg = UserChatMessage(role_name=self.role_name,
                                   role_type=RoleType.TOPIC, content=prompt)

        replies, terminated, info = self.step(chat_msg)
        if terminated or replies is None:
            raise ValueError(f"Collecting background failed due to {info}")

        self.update_messages(replies[0])
        self.topic.background = replies[0].content
        print(self.menu_color + self.topic.background)
        return self.topic.background

    def collect_pref(self, answer: str = None) -> Tuple[bool, str]:
        if answer is None:
            prompt = DebatePromptGenerator().get_collect_info_prompt()
            chat_msg = UserChatMessage(role_name=self.role_name,
                                       role_type=RoleType.TOPIC,
                                       content=prompt)
        else:
            chat_msg = UserChatMessage(role_name=self.role_name,
                                       role_type=RoleType.TOPIC,
                                       content=answer)

        replies, terminated, info = self.step(chat_msg)

        if terminated or replies is None:
            raise ValueError(f"Collecting information failed due to {info}")

        reply = replies[0]
        self.update_messages(reply)

        print(self.menu_color + reply.content + "\n")

        if "<QUESTION>" in reply.content or "QUESTION:" in reply.content:
            return (False, reply.content)

        elif "<SUMMARY>" in reply.content or "SUMMARY:" in reply.content:
            chat_msg = UserChatMessage(
                role_name=self.role_name, role_type=RoleType.TOPIC,
                content=DebatePromptGenerator().get_rephrase_sum_prompt())

            replies, terminated, info = self.step(chat_msg)
            if terminated or replies is None:
                raise ValueError(f"Rephrasing failed due to {info}")

            self.update_messages(replies[0])
            self.topic.preference = replies[0].content
            return (True, self.topic.preference)
        else:
            raise ValueError(
                f"Invalid reply, missing <QUESTION> or <SUMMARY>: {reply}")

    def start(self) -> None:

        self.reset()
        self.break_down_topic()
        self.specify_topic()
        self.collect_bg()

        my_input = ""
        n = 0
        while n < self.question_limit:
            n += 1
            if n == 1:
                (is_summary, content) = self.collect_pref()
            else:
                (is_summary, content) = self.collect_pref(my_input)

            if is_summary:
                print(self.topic.preference)
                break
            else:
                my_input = input(Fore.WHITE + "Please enter your answer : ")
