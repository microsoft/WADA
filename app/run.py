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

import argparse
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

import gradio as gr
import openai
import openai.error
import tenacity
from colorama import Fore
from utils import save_markdown_file, split_markdown_code

from wada.agents import TopicAgent
from wada.debate import Debate
from wada.typing import ModelType

ChatBotHistory = List[Tuple[Optional[str], Optional[str]]]

DEFAULT_TOPIC = "Living in Beijing or Chengdu?"


@dataclass
class State:
    topic_agent: Optional[TopicAgent]
    debate: Optional[Debate]
    chat: ChatBotHistory
    debate_history: ChatBotHistory
    ready_for_debate: bool

    @classmethod
    def empty(cls) -> 'State':
        return cls(None, None, [], [], False)

    @staticmethod
    def construct_inplace(state: 'State', topic_agent: Optional[TopicAgent],
                          session: Optional[Debate], chat: ChatBotHistory,
                          debate_history: ChatBotHistory,
                          ready_for_debate: bool = False):

        state.topic_agent = topic_agent
        state.debate = session
        state.chat = chat
        state.debate_history = debate_history
        state.ready_for_debate = ready_for_debate

    @staticmethod
    def export(state: 'State'):
        result = {
            'model': state.topic_agent.model.value,
            'topic': state.topic_agent.topic,
            'topic_pro': state.topic_agent.topic.pro,
            'topic_con': state.topic_agent.topic.con,
            'specified_aspects': state.topic_agent.topic.specified_aspects,
            'background': state.topic_agent.topic.background,
            'chat_history': state.chat,
            'preference': state.topic_agent.topic.preference,
            'debate_history': state.debate_history,
            'judgement': state.debate.host.judgement,
        }
        return result


def parse_arguments():
    """ Get command line arguments. """

    parser = argparse.ArgumentParser("WADA data explorer")
    parser.add_argument('--api-key', type=str, default=None,
                        help='OpenAI API key')
    parser.add_argument('--share', type=bool, default=False,
                        help='Expose the web UI to Gradio')
    parser.add_argument('--server-port', type=int, default=8080,
                        help='Port ot run the web page on')
    parser.add_argument('--inbrowser', type=bool, default=False,
                        help='Open the web UI in the default browser on lunch')
    parser.add_argument(
        '--concurrency-count', type=int, default=1,
        help='Number if concurrent threads at Gradio websocket queue. ' +
        'Increase to serve more requests but keep an eye on RAM usage.')
    args, unknown = parser.parse_known_args()
    if len(unknown) > 0:
        print("Unknown args: ", unknown)
    return args


def cleanup_on_launch(state) -> Tuple[State, Dict, Dict, Dict]:
    State.construct_inplace(state, None, None, [], [], False)
    return state, gr.update(interactive=False), gr.update(
        visible=True), gr.update(interactive=False)


def specify_topic(
    state: State,
    topic: str,
    model_type: str,
) -> Union[Dict, Tuple[State, str, Dict]]:

    try:
        model = ModelType.GPT_3_5_TURBO if model_type == "GPT 3.5" else ModelType.GPT_4
        topic_agent = TopicAgent(topic=topic, model=model)
        (pos, neg) = topic_agent.break_down_topic()
        print(pos, neg)
        specified_aspects = topic_agent.specify_topic()
        state.topic_agent = topic_agent

    except (openai.error.RateLimitError, tenacity.RetryError,
            RuntimeError) as ex:
        print("OpenAI API exception 0 " + str(ex))
        return (state, "", str(ex))

    return (state, specified_aspects, gr.update(visible=True))


def collect_bg(
    state: State
) -> Union[Dict, Tuple[State, str, ChatBotHistory, Dict, Dict]]:

    try:
        background = state.topic_agent.collect_bg()
        (is_summary, content) = state.topic_agent.collect_pref()
        if is_summary:
            raise RuntimeError("Not a question")
        state.chat.append((None, split_markdown_code(content)))
    except (openai.error.RateLimitError, tenacity.RetryError,
            RuntimeError) as ex:
        print("OpenAI API exception 0 " + str(ex))
        return state, str(ex), [], gr.update(), gr.update(visible=True)

    return state, background, gr.update(
        value=state.chat,
        visible=True), gr.update(visible=True), gr.update(interactive=True)


def submit_new_msg(
        state: State,
        reply: str) -> Union[Dict, Tuple[State, ChatBotHistory, Dict]]:

    state.chat.append((split_markdown_code(reply), None))
    return state, state.chat, gr.update(interactive=False)


def send_new_msg(
    state: State, reply: str
) -> Union[Dict, Tuple[State, Union[Dict, str], Union[Dict, str],
                       ChatBotHistory]]:

    try:
        (is_summary, content) = state.topic_agent.collect_pref(reply)
        if not is_summary:
            state.chat.append((None, split_markdown_code(content)))
            return [state, "", "", state.chat]
        else:
            state.ready_for_debate = True
            return (state, gr.update(visible=False),
                    gr.update(value=content, visible=True), state.chat)

    except (openai.error.RateLimitError, tenacity.RetryError,
            RuntimeError) as ex:
        print("OpenAI API exception 0 " + str(ex))
        return (state, str(ex), "", [])


def start_debate(
    state: State
) -> Union[Dict, Tuple[State, ChatBotHistory, str, Dict, Dict]]:
    try:
        if not state.ready_for_debate:
            return state, [], "", gr.update(interactive=True), gr.update()

        debate_session = Debate(topic=state.topic_agent.topic)

        intro_a = f"I am {debate_session.debater_a_name}, I will be arguing for: {state.topic_agent.topic.pro}"
        intro_b = f"I am {debate_session.debater_b_name}, I will be arguing for: {state.topic_agent.topic.con}"

        state.debate_history.append((split_markdown_code(intro_a), None))
        state.debate_history.append((None, split_markdown_code(intro_b)))

        state.debate = debate_session

        chat_turn_limit, n = 50, 0
        while n < chat_turn_limit:
            n += 1
            if n == 1:
                debater_a_return, debater_b_return = debate_session.init_chat()
            else:
                debater_a_return, debater_b_return = debate_session.step(
                    debater_b_reply)

            debater_a_reply, debater_a_terminated, debater_a_info = debater_a_return
            debater_b_reply, debater_b_terminated, debater_b_info = debater_b_return

            if debater_a_terminated:
                print(Fore.GREEN +
                      (f"{debate_session.debater_a_name} terminated. "
                       f"Reason: {debater_a_info['termination_reasons']}."))
                break
            if debater_b_terminated:
                print(Fore.GREEN +
                      (f"{debate_session.debater_b_name} terminated. "
                       f"Reason: {debater_b_info['termination_reasons']}."))
                break

            print(Fore.YELLOW + f"Round {n}\n")
            debater_a_reply_str = f"{debate_session.debater_a_name}:\n\n{debater_a_reply.content}\n"
            debater_b_reply_str = f"{debate_session.debater_b_name}:\n\n{debater_b_reply.content}\n"
            print(Fore.GREEN + debater_a_reply_str)
            print(Fore.BLUE + debater_b_reply_str)
            state.debate_history.append(
                (split_markdown_code(debater_a_reply.content), None))
            state.debate_history.append(
                (None, split_markdown_code(debater_b_reply.content)))

            if "DEBATE_TOPIC_DONE" in debater_b_reply.content or "DEBATE_TOPIC_DONE" in debater_a_reply.content:
                break

            shouldContinue, result = debate_session.host.step(
                debater_a_reply_str + debater_b_reply_str)

            if not shouldContinue:
                return state, state.debate_history, gr.update(
                    value=result, visible=True), gr.update(
                        interactive=True), gr.update(visible=True)

        return state, state.debate_history, gr.update(
            value="Reach limit",
            visible=True), gr.update(interactive=True), gr.update()

    except (openai.error.RateLimitError, tenacity.RetryError,
            RuntimeError) as ex:
        print("OpenAI API exception 0 " + str(ex))
        return state, [], "", gr.update(interactive=True), gr.update()


def update_state(state: State) -> Union[Dict, Tuple[State, ChatBotHistory]]:
    debate_cb_dict = dict()

    if state.ready_for_debate:
        debate_cb_dict['visible'] = True

    if state.debate_history is not None:
        debate_cb_dict['value'] = state.debate_history

    return (state, gr.update(**debate_cb_dict))


def change_topic(topic: str) -> Dict:
    if topic.strip() == "":
        return gr.update(interactive=False)
    else:
        return gr.update(interactive=True)


def refresh_page(state: State):
    state = State.empty()
    return (state, gr.update(interactive=True), gr.update(value=DEFAULT_TOPIC),
            gr.update(value="",
                      visible=False), gr.update(value="", visible=False),
            gr.update(value=[],
                      visible=False), gr.update(value="", visible=False),
            gr.update(value="",
                      visible=False), gr.update(value=[], visible=False),
            gr.update(value="", visible=False), gr.update(visible=False))


def save(state: State) -> None:
    result = State.export(state)
    save_markdown_file(result)


def main():
    """ Entry point. """

    args = parse_arguments()

    print("Getting Agents web server online...")

    demo.queue(args.concurrency_count) \
        .launch(share=True, inbrowser=args.inbrowser,
                server_name="127.0.0.1", server_port=args.server_port,
                debug=True)

    print("Exiting.")


css_str = "#start_button {border: 3px solid #4CAF50; font-size: 20px;}"

with gr.Blocks(css=css_str) as demo:
    gr.Markdown("# WADA")

    with gr.Row():
        with gr.Column(scale=4):
            model_type_dd = gr.Dropdown(["GPT 3.5", "GPT 4"], value="GPT 4",
                                        label="Model Type")

        with gr.Column(scale=4):
            start_bn = gr.Button("Start", elem_id="start_button")

            reset_bn = gr.Button("Reset", elem_id="reset_button")

    topic_ta = gr.TextArea(label="Give me a topic here", value=DEFAULT_TOPIC,
                           lines=1, interactive=True)

    topic_ta.change(change_topic, topic_ta, start_bn, queue=False)

    specified_aspects_ta = gr.TextArea(
        label="Specified aspects of information of the topic", lines=1,
        interactive=False, visible=False)

    topic_background_ta = gr.TextArea(label="Generated background information",
                                      lines=1, interactive=False,
                                      visible=False)

    interact_cb = gr.Chatbot(label="Chat between you and the agent",
                             visible=False)

    reply_tb = gr.Textbox(show_label=False,
                          placeholder="Enter text and press enter",
                          visible=False).style(container=False)

    topic_preference_ta = gr.TextArea(label="Preference summary", lines=1,
                                      interactive=False, visible=False)

    debate_cb = gr.Chatbot(label="Chat between autonomous debaters",
                           visible=False)

    decision_ta = gr.TextArea(label="Suggestion", lines=1, interactive=False,
                              visible=False)

    save_bn = gr.Button("Save", elem_id="save_button", visible=False)

    topic_catagory_dd = gr.Dropdown([
        "Career and Education", "Personal Relationships",
        "Lifestyle and Health", "Ethical and Moral Dilemmas",
        "Financial Decisions", "Other"
    ], max_choices=1, value="Career and Education", label="Topic Catagory")

    state = gr.State(State.empty())

    save_bn.click(save, state, queue=False)

    start_bn.click(cleanup_on_launch, state,
                   [state, start_bn, specified_aspects_ta, reset_bn],
                   queue=False) \
        .then(specify_topic,
              [state, topic_ta, topic_catagory_dd],
              [state, specified_aspects_ta, topic_background_ta],
              queue=False) \
        .then(collect_bg, state,
              [state, topic_background_ta, interact_cb, reply_tb, reset_bn],
              queue=False)

    reply_tb.submit(submit_new_msg,
                    [state, reply_tb],
                    [state, interact_cb, reset_bn]) \
        .then(send_new_msg,
              [state, reply_tb],
              [state, reply_tb, topic_preference_ta, interact_cb],
              queue=False) \
        .then(start_debate,
              state,
              [state, debate_cb, decision_ta, reset_bn, save_bn],
              queue=False)

    demo.load(update_state, state, [state, debate_cb], every=0.5)

    reset_bn.click(refresh_page, state, [
        state, start_bn, topic_ta, specified_aspects_ta, topic_background_ta,
        interact_cb, reply_tb, topic_preference_ta, debate_cb, decision_ta,
        save_bn
    ], queue=False)

if __name__ == "__main__":

    main()
