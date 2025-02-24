# ATENCAO: ESTE CÓDIGO DEVE SER EXECUTADO UMA VEZ. NÃO INCLUA ELE NO main.py NEM NO SERVIDOR!
# Te explico melhor na parte 4 : https://youtube.com/playlist?list=PLgq2T1anEfKd3u-cwLZYoMCTPHoKgQIIp&si=vLXuqKd5qQZbBG99
from os import getenv
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

OPENAI_KEY = getenv("OPENAI_KEY")


def generate_blog_titles(api_key: str, num_posts: int) -> list[str]:
    client = OpenAI(api_key=api_key)

    prompt = f"""
    Gere exatamente {num_posts} ideias criativas de temas para posts de blog. 
    A resposta deve ser um JSON válido com a chave 'themes'.
    As ideias devem ser interessantes e voltadas para tecnologia e desenvolvimento de software. 
    Não repita os temas.
    Apenas os títulos, sem numeração, sem introduções ou explicações adicionais.
    Não inclua nenhuma explicação ou texto adicional na resposta, apenas o array JSON.
    """

    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente especializado em criar ideias de temas para blogs.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        response = chat_completion.choices[0].message.content

        cost_per_token_usd = 0.150 / 1_000_000

        price_brl = chat_completion.usage.total_tokens * cost_per_token_usd * 6
        print(f"R$ {price_brl}")
        return {
            "themes": response,
            "price": price_brl,
        }

    except Exception as e:
        print(f"Erro ao gerar temas de blog: {e}")
        return {
            "themes": [],
            "price": 0.0,
        }


# Exemplo de uso
if __name__ == "__main__":
    num_posts = 30
    response = generate_blog_titles(api_key=OPENAI_KEY, num_posts=num_posts)
    blog_titles = response["themes"]
    price = response["price"]

    print("Temas gerados:", blog_titles)
    print("Custo total (R$):", price)

    json_formated = json.loads(blog_titles)
    print("Quantidade de temas gerados:", len(json_formated["themes"]))