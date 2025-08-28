from google.adk.agents import LlmAgent

from utilities.consul_agent import ConsulEnabledAIAgent


class OrchestratorAgent(ConsulEnabledAIAgent):

    def build_agent(self) -> LlmAgent:
        """
        Construct the Gemini-based LlmAgent with tools
        """
        self._set_orchestrator(True)
        ai_agent = LlmAgent(
            model="gemini-2.5-flash-latest",
            name="orchestrator_agent",
            description="Delegates user queries to child A2A agents based on intent.",
            instruction=self._root_instruction,
            tools=self._get_llm_tools()
        )
        return ai_agent
