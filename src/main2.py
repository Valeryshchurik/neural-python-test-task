import os
from langchain_openai import ChatOpenAI

MY_BASE_KEY = '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'
# Установите переменную окружения OPENAI_API_KEY со своим ключом
os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"

def main():
    # Создаем инстанс модели из langchain-openai
    chat_model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    # Пример запроса к модели
    response = chat_model.invoke({"input": "Привет, как дела?"})

    # Выводим ответ модели
    print(response)

if __name__ == "__main__":
    main()