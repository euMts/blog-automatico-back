import requests
from openai import OpenAI

# https://api.telegram.org/bot<API_KEY>/getUpdates -> pegar chat ID do telegram


def send_telegram_success_message(
    api_key, chat_id, inserted_id, theme_name, execution_time, blog_post_total_cost_brl, blog_posts_url
):
    try:
        url = f"https://api.telegram.org/bot{api_key}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": f"🟢 Novo post no blog!\n💡 Tema: {theme_name}\n⏰ Tempo de execução: {execution_time:.2f} segundos.\n💸 Custo OpenAI: R$ {blog_post_total_cost_brl}",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": "Acesse clicando aqui",
                            "url": f"{blog_posts_url}{inserted_id}",
                        }
                    ]
                ]
            },
        }

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            print(f"Erro ao enviar mensagem: {response.status_code}, {response.text}")
            return None

        print("Mensagem enviada com sucesso!")
        return response.status_code

    except requests.exceptions.RequestException as req_err:
        print(f"Erro de rede ao enviar mensagem: {req_err}")
        return None

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None


def send_telegram_common_message(api_key, chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{api_key}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
        }

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            print(f"Erro ao enviar mensagem: {response.status_code}, {response.text}")
            return None

        print("Mensagem enviada com sucesso!")
        return response.status_code

    except requests.exceptions.RequestException as req_err:
        print(f"Erro de rede ao enviar mensagem: {req_err}")
        return None

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None


def get_blog_post_openai(api_key: str, theme: str) -> str:
    client = OpenAI(api_key=api_key)

    prompt = f"""
    Escreva um post de blog bem estruturado em Markdown sobre o tema: "{theme}".
    Utilize uma linguagem fácil de entender, com exemplos, e seja técnico quando for necessário. 
    O post deve conter:
    - Um título principal.
    - Uma introdução interessante.
    - Pelo menos 3 seções com subtítulos.
    - Um parágrafo de conclusão.
    Certifique-se de usar formatação de Markdown adequada.
    """

    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente especializado em escrever conteúdo para blogs de tecnologia.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
        )

        blog_post = chat_completion.choices[0].message.content

        total_tokens = chat_completion.usage.total_tokens

        cost_per_token_usd = (
            0.150 / 1_000_000
        )  # ($0.150 por 1M tokens) | gpt-4o-mini | https://openai.com/api/pricing/
        total_cost_usd = total_tokens * cost_per_token_usd

        usd_to_brl_exchange_rate = 5.90
        total_cost_brl = total_cost_usd * usd_to_brl_exchange_rate

        return {
            "blog_post": blog_post,
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost_usd,
            "total_cost_brl": total_cost_brl,
        }

    except Exception as e:
        print(f"Erro ao gerar post de blog: {e}")
        return None
