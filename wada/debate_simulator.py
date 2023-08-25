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

from typing import Dict, Optional, Tuple

from colorama import Fore

from wada.agents.debater_agent import DebaterAgent
from wada.generators import SystemMessageGenerator
from wada.messages import UserChatMessage
from wada.topic import Topic
from wada.typing import ModelType, RoleType

from .agents.host_agent import HostAgent


class DebateSimulator:
    r"""Simulate a debate between two agents with search ability.

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
        verbose (bool, optional): Whether to print the debate to the console.
            (default: :obj:`False`)
    """

    def __init__(
        self,
        topic: Topic,
        debater_a_name: str = "Proposition",
        debater_b_name: str = "Contradiction",
        host_name: str = "Host",
        turn_limit: int = 10,
        with_host_in_the_loop: bool = True,
        model_type: ModelType = ModelType.GPT_4,
        debater_a_agent_kwargs: Optional[Dict] = None,
        debater_b_agent_kwargs: Optional[Dict] = None,
        host_kwargs: Optional[Dict] = None,
        verbose: bool = False,
    ) -> None:
        self.topic = topic

        self.debater_a_name = debater_a_name
        self.debater_b_name = debater_b_name
        self.host_name = host_name

        self.with_host_in_the_loop = with_host_in_the_loop
        self.model_type = model_type

        self.turn_limit = turn_limit
        self.round = 0
        self.terminated = False

        self.history = []

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

        self.debater_a_agent = DebaterAgent(
            sys_msg_dict={
                "stance": self.topic.pro,
                **sys_msg_meta_dict
            }, verbose=verbose, **(debater_a_agent_kwargs or {}))

        self.debater_b_agent = DebaterAgent(
            sys_msg_dict={
                "stance": self.topic.con,
                **sys_msg_meta_dict
            }, verbose=verbose, **(debater_b_agent_kwargs or {}))

    def reset(self) -> None:
        self.debater_a_agent.reset()
        self.debater_b_agent.reset()
        self.round = 0
        self.terminated = False
        self.history = [
            UserChatMessage(
                role_name=self.host_name,
                role_type=RoleType.HOST,
                content="Now give me your first argument and explanation")
        ]

    def step(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        if self.terminated:
            return (None, None, None)

        self.round += 1

        if self.round > self.turn_limit:
            self.terminated = True
            return (None, None, None)

        debater_a_msg = self.history[-1].content
        debater_a_reply = self.debater_a_agent.step(input=debater_a_msg)
        debater_b_reply = self.debater_b_agent.step(input=debater_a_reply)

        self.history.append(
            UserChatMessage(role_name=self.debater_a_name,
                            role_type=RoleType.DEBATER,
                            content=debater_a_reply))
        self.history.append(
            UserChatMessage(role_name=self.debater_b_name,
                            role_type=RoleType.DEBATER,
                            content=debater_b_reply))

        print(Fore.YELLOW + f"Round {self.round}\n")
        debater_a_reply_str = f"{self.debater_a_name}:\n\n{debater_a_reply}\n"
        debater_b_reply_str = f"{self.debater_b_name}:\n\n{debater_b_reply}\n"
        print(Fore.GREEN + debater_a_reply_str)
        print(Fore.BLUE + debater_b_reply_str)

        if "DEBATE_TOPIC_DONE" in debater_a_reply or "DEBATE_TOPIC_DONE" in debater_b_reply:
            self.terminated = True

        if self.with_host_in_the_loop:
            debate_continue, judge_result = self.host.step(
                debater_a_reply_str + debater_b_reply_str)
            if not debate_continue:
                self.terminated = True
        else:
            judge_result = None
        return (debater_a_reply, debater_b_reply, judge_result)
