Repository contains prepared processors for llm file parsing service using LangChain. Two processors represented here:

a) Synchronous processor that uses a basic method for linking chain elements
b) Asynchronous processor that is based on using langgraph.

Processors take data from /data folder and save the processing result to /result folder

### Setup steps:
#### prepare the env
1. ```make env```
2. pass the OPENAI_API_KEY to .env

#### build docker image
3. ```make build```

#### start llm_processing
4. a) ```make start_sync_mode``` for SyncChainFileProcessor
   b) ```make start_async_mode``` for AsyncGraphFileProcessor

#### to run tests use ```make test```
#### to clean the output dir you can use ```make clean```

### Local work:
If you want to run project locally, you need to install poetry and run

```poetry install```

then you will be able to run sync_processor simply by running the sync_starter.py or async_starter.py
For example
```commandline
cd src
python -m starters.sync_starter
```

to run tests locally you can just call

```pytest```
