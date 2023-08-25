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

from typing import Dict, List, Optional, Tuple

from wada.agents import ChatAgent
from wada.generators import SystemMessageGenerator
from wada.messages import ChatMessage, UserChatMessage
from wada.topic import Topic
from wada.typing import ModelType, RoleType

from .agents.host_agent import HostAgent


class Debate:
    r"""Simulate a debate between two agents.

    Args:
        topic (Topic): The topic of the debate.
        debater_a_name (str): The name of the first debater.
            (default: :obj:`"Proposition"`)
        debater_b_name (str): The name of the second debater.
            (default: :obj:`"Contradiction"`)
        host_name (str): The name of the the host.
            (default: :obj:`"Host"`)
        turn_limit (int): The maximum number of turns.
            (fefault: :obj:`10`)
        with_host_in_the_loop (bool, optional): Whether to include a host
            in the loop. (default: :obj:`False`)
        model_type (ModelType, optional): The type of GPT model to use.
            (default: :obj:`ModelType.GPT_4`)
        debater_a_agent_kwargs (Dict, optional): Additional arguments to pass
            to the debater A agent. (default: :obj:`None`)
        debater_b_agent_kwargs (Dict, optional): Additional arguments to pass
            to the debater B agent. (default: :obj:`None`)
        host_kwargs (Dict, optional): Additional arguments to pass to the
            host. (default: :obj:`None`)
    """

    def __init__(
        self,
        topic: Topic,
        debater_a_name: str = "Proposition",
        debater_b_name: str = "Contradiction",
        host_name: str = "Host",
        with_host_in_the_loop: bool = True,
        model_type: ModelType = ModelType.GPT_4,
        debater_a_agent_kwargs: Optional[Dict] = None,
        debater_b_agent_kwargs: Optional[Dict] = None,
        host_kwargs: Optional[Dict] = None,
    ) -> None:

        self.debater_a_name = debater_a_name
        self.debater_b_name = debater_b_name
        self.host_name = host_name

        self.with_host_in_the_loop = with_host_in_the_loop
        self.model_type = model_type

        self.topic = topic

        self.debater_a_agent_kwargs = debater_a_agent_kwargs
        self.debater_b_agent_kwargs = debater_b_agent_kwargs

        if with_host_in_the_loop:
            host_sys_msg = SystemMessageGenerator().from_dict(
                dict(topic=self.topic.content, summary=self.topic.preference,
                     aspects=self.topic.specified_aspects),
                role_tuple=(host_name, RoleType.HOST),
            )
            self.host = HostAgent(
                host_sys_msg,
                model_type,
                **(host_kwargs or {}),
                role_name=host_name,
            )
        else:
            self.host = None

        sys_msg_meta_dict = dict(topic=self.topic.content)
        if self.with_host_in_the_loop and self.host is not None:
            sys_msg_meta_dict["background"] = self.topic.background
            sys_msg_meta_dict["summary"] = self.topic.preference

        self.debater_a_sys_msg = SystemMessageGenerator().from_dict(
            meta_dict={
                "position": self.topic.pro,
                **sys_msg_meta_dict
            }, role_tuple=(self.debater_a_name, RoleType.DEBATER))

        self.debater_b_sys_msg = SystemMessageGenerator().from_dict(
            meta_dict={
                "position": self.topic.con,
                **sys_msg_meta_dict
            }, role_tuple=(self.debater_b_name, RoleType.DEBATER))

        self.debater_a_agent = ChatAgent(
            self.debater_a_sys_msg,
            self.model_type,
            **(self.debater_a_agent_kwargs or {}),
        )

        self.debater_b_agent = ChatAgent(
            self.debater_b_sys_msg,
            self.model_type,
            **(self.debater_b_agent_kwargs or {}),
        )

    def init_chat(
        self
    ) -> Tuple[Tuple[Optional[ChatMessage], Optional[bool], Optional[Dict]],
               Tuple[Optional[ChatMessage], Optional[bool], Optional[Dict]]]:
        self.debater_a_agent.reset()
        self.debater_b_agent.reset()

        debater_a_msg = UserChatMessage(
            role_name=self.debater_a_sys_msg.role_name,
            role_type=self.debater_a_sys_msg.role_type,
            content=("Now give me your first argument and explanation"))

        return self.step(debater_a_msg)

    def process_messages(
        self,
        messages: List[ChatMessage],
    ) -> ChatMessage:
        if len(messages) == 0:
            raise ValueError("No messages to process.")
        if len(messages) > 1 and not self.with_host_in_the_loop:
            raise ValueError("Got more than one message to process. "
                             f"Num of messages: {len(messages)}.")
        else:
            processed_msg = messages[0]
            processed_msg.content = processed_msg.content.replace("###", "")

        return processed_msg

    def step(
        self,
        debater_a_msg: ChatMessage,
    ) -> Tuple[Tuple[Optional[ChatMessage], Optional[bool], Optional[Dict]],
               Tuple[Optional[ChatMessage], Optional[bool], Optional[Dict]]]:

        debater_a_replies, debater_a_terminated, debater_a_info = self.debater_a_agent.step(
            debater_a_msg.to_user_chat_message())
        if debater_a_terminated or debater_a_replies is None:
            return (None, debater_a_terminated, debater_a_info), (None, None,
                                                                  None)
        debater_a_reply = self.process_messages(debater_a_replies)
        self.debater_a_agent.update_messages(debater_a_reply)

        debater_b_replies, debater_b_terminated, debater_b_info = self.debater_b_agent.step(
            debater_a_reply.to_user_chat_message())
        if debater_b_terminated or debater_b_replies is None:
            return (None, debater_a_terminated,
                    debater_a_info), (None, debater_b_terminated,
                                      debater_b_info)
        debater_b_reply = self.process_messages(debater_b_replies)
        self.debater_b_agent.update_messages(debater_b_reply)

        return ((debater_a_reply, debater_a_terminated, debater_a_info),
                (debater_b_reply, debater_b_terminated, debater_b_info))
