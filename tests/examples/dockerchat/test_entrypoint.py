from llmagent.agent.base import AgentConfig
from llmagent.language_models.openai_gpt import OpenAIGPTConfig, OpenAIChatModel
from examples.dockerchat.dockerchat_agent_messages import EntryPointAndCMDMessage
from llmagent.utils.configuration import update_global_settings, Settings, set_global
from llmagent.agent.chat_agent import ChatAgent
from llmagent.prompts.prompts_config import PromptsConfig
from llmagent.parsing.parser import ParsingConfig
from llmagent.cachedb.redis_cachedb import RedisCacheConfig


class MessageHandlingAgent(ChatAgent):
    def find_entrypoint(self, EntryPointAndCMDMessage) -> str:
        return CODE_CHAT_RESPONSE_FIND_ENTRY


cfg = AgentConfig(
    debug=False,
    vecdb=None,
    llm=OpenAIGPTConfig(
        type="openai",
        chat_model=OpenAIChatModel.GPT3_5_TURBO,
        cache_config=RedisCacheConfig(fake=False),
    ),
)

FIND_ENTRYPOINT_MSG = """
great, please tell me this --
{
'request': 'find_entrypoint'
}/if you know it
"""

CODE_CHAT_RESPONSE_FIND_ENTRY = """
The name of the main script in this repo is main.py. To run it, you can use the command python main.py
"""

cfg = AgentConfig(
    debug=True,
    name="test-llmagent",
    vecdb=None,
    llm=OpenAIGPTConfig(
        type="openai",
        chat_model=OpenAIChatModel.GPT4,
        cache_config=RedisCacheConfig(fake=False),
    ),
    parsing=ParsingConfig(),
    prompts=PromptsConfig(),
)
agent = MessageHandlingAgent(cfg)


def test_enable_message():
    agent.enable_message(EntryPointAndCMDMessage)
    assert "find_entrypoint" in agent.handled_classes
    assert agent.handled_classes["find_entrypoint"] == EntryPointAndCMDMessage


def test_disable_message():
    agent.enable_message(EntryPointAndCMDMessage)

    agent.disable_message(EntryPointAndCMDMessage)
    assert "find_entrypoint" not in agent.handled_classes


def test_dockerchat_agent_handle_message():
    """
    Test whether messages are handled correctly, and that
    message enabling/disabling works as expected.
    """
    agent.enable_message(EntryPointAndCMDMessage)
    agent.disable_message(EntryPointAndCMDMessage)
    assert agent.handle_message(FIND_ENTRYPOINT_MSG) is None


def test_llm_agent_message(test_settings: Settings):
    """
    Test whether LLM is able to generate message in required format, and the
    agent handles the message correctly.
    """
    set_global(test_settings)
    update_global_settings(cfg, keys=["debug"])
    agent = MessageHandlingAgent(cfg)
    agent.enable_message(EntryPointAndCMDMessage)

    llm_msg = agent.respond_forget(
        """Start by asking me about the identifying main scripts and 
        their argument in the repo to define the ENTRYPOINT."""
    ).content

    agent_result = agent.handle_message(llm_msg)
    assert agent_result == CODE_CHAT_RESPONSE_FIND_ENTRY