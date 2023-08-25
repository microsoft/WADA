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

from typing import Any, Optional, Tuple

from colorama import Fore

from wada.agents import ChatAgent
from wada.messages import SystemMessage, UserChatMessage
from wada.typing import ModelType, RoleType


class HostAgent(ChatAgent):
    r"""A chat agent that can act as a host in a debate.

    Args:
        system_message (SystemMessage): The system message of chat.
        model (ModelType): The model type to use for the agent.
            (default: :obj:`ModelType.GPT_4`)
        message_window_size (Optional[int]): The maximum number of messages
            to use for the agent's message window. If :obj:`None`, then
            the message window size is unlimited. (default: :obj:`6`)
        menu_color (Any): The output color in console.
            (default: :obj:`Fore.MAGENTA`)
        role_name (str): The role name of the agent.
            (default: :obj:`"Host"`)
    """

    def __init__(
        self,
        system_message: SystemMessage,
        model: ModelType = ModelType.GPT_4,
        message_window_size: int = 6,
        menu_color: Any = Fore.MAGENTA,
        role_name: str = "Host",
    ) -> None:
        super().__init__(system_message, model=model,
                         message_window_size=message_window_size)
        self.menu_color = menu_color
        self.role_name = role_name
        self.judgement = ""

    def step(self, messages: str) -> Tuple[bool, Optional[str]]:
        chat_msg = UserChatMessage(role_name=self.role_name,
                                   role_type=RoleType.HOST, content=messages)
        replies, terminated, info = super().step(chat_msg)
        if terminated or replies is None:
            raise ValueError(f"Ready to judge failed due to {info}")

        reply = replies[0]
        self.update_messages(reply)
        print(self.menu_color, reply.content)

        if "CONTINUE" in reply.content:
            return (True, reply.content)
        elif "END" in reply.content:
            self.judgement = reply.content.replace("<<<END>>>", "").strip()
            return (False, self.judgement)
        else:
            raise ValueError(f"Invalid reply during judging: {reply}")
