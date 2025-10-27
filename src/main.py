from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

def analyze_file_content(file_content: str, llm: ChatOpenAI):
    # Пример шаблона, который извлекает из текста файл авторов и лицензию
    copyright_prompt = PromptTemplate(
        template=(
            "Извлеки из данного текста:\n"
            "- copyright holder\n"
            "- license name\n"
            "Если лицензия разрешительная (не GPL и похожие), то перечисли функции с количеством аргументов.\n"
            "Если лицензия копилефт (GPL и похожие):\n"
            "  - если функций больше 2, перечисли функции с количеством аргументов,\n"
            "  - иначе перепиши файл на Rust.\n"
            "Ответь ТОЛЬКО одним JSON объектом без дополнительных рассуждений, размышлений или меток.\n\n"
            "Текст файла:\n{file_content}"
        ),
        input_variables=["file_content"]
    )
    chain = copyright_prompt | llm
    result = chain.invoke({"file_content": file_content})
    return result

def main():
    print('HELLLLLLLLLLLLLLLLLLLLLO')
    MY_BASE_KEY = 'sk-or-v1-'
    llm = ChatOpenAI(
        temperature=0,
        model_name="minimax/minimax-m2:free",
        openai_api_base="https://openrouter.ai/api/v1",
        api_key=MY_BASE_KEY
    )
    # prompt = PromptTemplate(template="Определите слово: {word}", input_variables=["word"])
    # chain = prompt | llm
    # result = chain.invoke({"word": "Python"})
    # print(result)
    # Пример чтения файла (замените на ваши пути к файлам из data/)
    with open("../data/1.py", "r", encoding="utf-8") as f:
        file_content = f.read()

    analysis = analyze_file_content(file_content, llm)
    print(analysis)



if __name__ == "__main__":
    main()
