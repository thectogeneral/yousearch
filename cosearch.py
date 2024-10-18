import glob

def RAG():
    requirement_dependency = [
        "openai",
    ]

    extra_files = glob.glob("ui/**/*", recursive=True)

    deployment_template = {
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

handler_max_concurrency = 16


if __name__ == "__main__":
    rag = RAG()
    #rag.launch()