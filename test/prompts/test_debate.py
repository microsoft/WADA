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

from wada.prompts import DebatePromptTemplateDict, TextPrompt


def test_debate_prompt_template_dict():
    template_dict = DebatePromptTemplateDict()

    assert isinstance(template_dict.DEBATER_PROMPT, TextPrompt)
    assert isinstance(template_dict.HOST_DECISION_PROMPT, TextPrompt)
    assert isinstance(template_dict.HOST_JUDGE_PROMPT, TextPrompt)
    assert isinstance(template_dict.HOST_PROMPT, TextPrompt)
    assert isinstance(template_dict.TOPIC_BREAK_DOWN_PROMPT, TextPrompt)
    assert isinstance(template_dict.TOPIC_COLLECT_BG_PROMPT, TextPrompt)
    assert isinstance(template_dict.TOPIC_COLLECT_INFO_PROMPT, TextPrompt)
    assert isinstance(template_dict.TOPIC_REPHRASE_SUM_PROMPT, TextPrompt)
    assert isinstance(template_dict.TOPIC_SPECIFY_PROMPT, TextPrompt)
