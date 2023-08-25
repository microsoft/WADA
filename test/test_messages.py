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

from wada.messages import BaseMessage, SystemMessage
from wada.typing import RoleType


def test_base_message():
    role_name = "test_role_name"
    role_type = RoleType.DEFAULT
    meta_dict = {"key": "value"}
    role = "user"
    content = "test_content"

    message = BaseMessage(role_name=role_name, role_type=role_type,
                          meta_dict=meta_dict, role=role, content=content)

    assert message.role_name == role_name
    assert message.role_type == role_type
    assert message.meta_dict == meta_dict
    assert message.role == role
    assert message.content == content

    user_message = message.to_user_chat_message()
    assert user_message.role_name == role_name
    assert user_message.role_type == role_type
    assert user_message.meta_dict == meta_dict
    assert user_message.role == "user"
    assert user_message.content == content

    openai_message = message.to_openai_message()
    assert openai_message == {"role": role, "content": content}

    dictionary = message.to_dict()
    assert dictionary == {
        "role_name": role_name,
        "role_type": role_type.name,
        **(meta_dict or {}), "role": role,
        "content": content
    }


def test_system_message():
    role_name = "test_role_name"
    role_type = RoleType.DEFAULT
    meta_dict = {"key": "value"}
    content = "test_content"

    message = SystemMessage(role_name=role_name, role_type=role_type,
                            meta_dict=meta_dict, content=content)

    assert message.role_name == role_name
    assert message.role_type == role_type
    assert message.meta_dict == meta_dict
    assert message.role == "system"
    assert message.content == content

    dictionary = message.to_dict()
    assert dictionary == {
        "role_name": role_name,
        "role_type": role_type.name,
        **(meta_dict or {}), "role": "system",
        "content": content
    }
