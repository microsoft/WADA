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

from dataclasses import dataclass
from typing import Dict, Optional, Union

from .typing import RoleType

OpenAISystemMessage = Dict[str, str]
OpenAIAssistantMessage = Dict[str, str]
OpenAIUserMessage = Dict[str, str]
OpenAIChatMessage = Union[OpenAIUserMessage, OpenAIAssistantMessage]
OpenAIMessage = Union[OpenAISystemMessage, OpenAIChatMessage]


@dataclass
class BaseMessage:
    r"""Base class for message objects.

    Args:
        role_name (str): The name of the role.
        role_type (RoleType): The type of role.
        meta_dict (Optional[Dict[str, str]]): Additional metadata dictionary
            for the message.
        role (str): The role of the message in OpenAI chat system, either
            :obj:`"system"`, :obj:`"user"`, or :obj:`"assistant"`.
        content (str): The content of the message.
    """
    role_name: str
    role_type: RoleType
    meta_dict: Optional[Dict[str, str]]
    role: str
    content: str

    def to_user_chat_message(self) -> "UserChatMessage":
        return UserChatMessage(
            role_name=self.role_name,
            role_type=self.role_type,
            meta_dict=self.meta_dict,
            content=self.content,
        )

    def to_openai_message(self, role: Optional[str] = None) -> OpenAIMessage:
        role = role or self.role
        if role not in {"system", "user", "assistant"}:
            raise ValueError(f"Unrecognized role: {role}")
        return {"role": role, "content": self.content}

    def to_dict(self) -> Dict:
        return {
            "role_name": self.role_name,
            "role_type": self.role_type.name,
            **(self.meta_dict or {}),
            "role": self.role,
            "content": self.content,
        }

@dataclass
class SystemMessage(BaseMessage):
    role_name: str
    role_type: RoleType
    meta_dict: Optional[Dict[str, str]] = None
    role: str = "system"
    content: str = ""

@dataclass
class ChatMessage(BaseMessage):
    role_name: str
    role_type: RoleType
    meta_dict: Optional[Dict[str, str]]
    role: str
    content: str = ""

@dataclass
class UserChatMessage(ChatMessage):
    role_name: str
    role_type: RoleType
    meta_dict: Optional[Dict[str, str]] = None
    role: str = "user"
    content: str = ""


MessageType = Union[BaseMessage, SystemMessage, ChatMessage, UserChatMessage]
