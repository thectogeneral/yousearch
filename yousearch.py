import glob


import leptonai
from leptonai import Client
from leptonai.kv import KV
from leptonai.photon import Photon, StaticFiles
from leptonai.photon.types import to_bool
from leptonai.api.workspace import WorkspaceInfoLocalRecord
from leptonai.util import tool

class RAG():
    def __init__(self):
        self.requirement_dependency = [
            "openai",
        ]
        self.extra_files = glob.glob("ui/**/*", recursive=True)
        self.deployment_template = {
            "resource_shape": "cpu.small",
            "env": {
                "BACKEND": "LEPTON",
                "GOOGLE_SEARCH_CX": "",
                "LLM_MODEL": "mixtral-8x7b",
                "KV_NAME": "search-with-lepton",
                "RELATED_QUESTIONS": "true",
                "LEPTON_ENABLE_AUTH_BY_COOKIE": "true",
            },
            "secret": [
                "BING_SEARCH_V7_SUBSCRIPTION_KEY",
                "GOOGLE_SEARCH_API_KEY",
                "SERPER_SEARCH_API_KEY",
                "SEARCHAPI_API_KEY",
                "LEPTON_WORKSPACE_TOKEN",
            ],
        }
        self.handler_max_concurrency = 16
        self.init()

    def init(self):
        """
        Initializes photon configs.
        """
        # First, log in to the workspace.
        leptonai.api.workspace.login()
        self.backend = os.environ["BACKEND"].upper()
        if self.backend == "LEPTON":
            self.leptonsearch_client = Client(
                "https://search-api.lepton.run/",
                token=os.environ.get("LEPTON_WORKSPACE_TOKEN")
                or WorkspaceInfoLocalRecord.get_current_workspace_token(),
                stream=True,
                timeout=httpx.Timeout(connect=10, read=120, write=120, pool=10),
            )
        elif self.backend == "BING":
            self.search_api_key = os.environ["BING_SEARCH_V7_SUBSCRIPTION_KEY"]
            self.search_function = lambda query: search_with_bing(
                query,
                self.search_api_key,
            )
        elif self.backend == "GOOGLE":
            self.search_api_key = os.environ["GOOGLE_SEARCH_API_KEY"]
            self.search_function = lambda query: search_with_google(
                query,
                self.search_api_key,
                os.environ["GOOGLE_SEARCH_CX"],
            )
        elif self.backend == "SERPER":
            self.search_api_key = os.environ["SERPER_SEARCH_API_KEY"]
            self.search_function = lambda query: search_with_serper(
                query,
                self.search_api_key,
            )
        elif self.backend == "SEARCHAPI":
            self.search_api_key = os.environ["SEARCHAPI_API_KEY"]
            self.search_function = lambda query: search_with_searchapi(
                query,
                self.search_api_key,
            )
        else:
            raise RuntimeError("Backend must be LEPTON, BING, GOOGLE, SERPER or SEARCHAPI.")
        self.model = os.environ["LLM_MODEL"]

        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.handler_max_concurrency * 2
        )
        # Create the KV to store the search results.
        logger.info("Creating KV. May take a while for the first time.")
        self.kv = KV(
            os.environ["KV_NAME"], create_if_not_exists=True, error_if_exists=False
        )
        # whether we should generate related questions.
        self.should_do_related_questions = to_bool(os.environ["RELATED_QUESTIONS"])


if __name__ == "__main__":
    rag = RAG()
    rag.launch()