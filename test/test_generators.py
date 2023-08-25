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

from wada.generators import (
    DebatePromptGenerator,
    DebatePromptTemplateGenerator,
    SystemMessageGenerator,
)
from wada.messages import SystemMessage
from wada.prompts import TextPrompt
from wada.typing import RoleType


def test_system_message_generator():
    generator = SystemMessageGenerator()
    sys_msg = generator.from_dict(
        dict(topic="A or B?", position="AAA", background="Not available",
             summary="No preference"),
        role_tuple=("debater test", RoleType.DEBATER))

    assert isinstance(sys_msg, SystemMessage)
    assert isinstance(sys_msg.content, str)
    assert sys_msg.role_name == "debater test"
    assert sys_msg.role_type == RoleType.DEBATER
    assert sys_msg.role == "system"


def test_debate_prompt_generator():
    generator = DebatePromptGenerator()
    topic = "To be or not to be?"
    debate_topic_prompt = generator.get_topic_specify_prompt(topic)

    assert isinstance(debate_topic_prompt, TextPrompt)
    assert topic in debate_topic_prompt


def test_debate_prompt_template_generator():
    generator = DebatePromptTemplateGenerator()
    sys_msg_template = generator.get_sys_msg_prompt_template()

    assert isinstance(sys_msg_template, str)
    assert "topic" in sys_msg_template
    assert "tool_names" in sys_msg_template
