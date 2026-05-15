import os
import socket
import logging
import requests
import ast
import operator
import threading
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv


env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
CLIENT_TIMEOUT = float(os.getenv("CLIENT_TIMEOUT", "30"))


ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}

ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/server.log",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def validate_token(token):
    try:
        url = f"{SUPABASE_URL}/auth/v1/user"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return False, f"token inválido ou usuário não autorizado: {response.status_code} - {response.text}"

        user_data = response.json()
        user_id = user_data.get("id")
        email = user_data.get("email")
        role = user_data.get("role", "authenticated")

        if not user_id:
            return False, "id do usuário ausente"

        return True, {
            "user_id": user_id,
            "email": email,
            "role": role
        }

    except Exception as e:
        return False, f"erro ao validar token no Supabase: {e}"


def save_to_supabase(command, response, client_ip, auth_user=None):
    url = f"{SUPABASE_URL}/rest/v1/command_logs"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    payload = {
        "command": command,
        "response": response,
        "client_ip": client_ip,
        "user_id": auth_user.get("user_id") if auth_user else None,
        "email": auth_user.get("email") if auth_user else None,
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        logging.info(f"Supabase status={r.status_code}")
        r.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Erro ao salvar no Supabase: {e}")


def eval_ast(node):
    if isinstance(node, ast.Expression):
        return eval_ast(node.body)
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"constante não permitida: {node.value}")
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in ALLOWED_OPERATORS:
            raise ValueError(f"operador não permitido: {op_type.__name__}")
        left = eval_ast(node.left)
        right = eval_ast(node.right)
        return ALLOWED_OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in ALLOWED_UNARY_OPERATORS:
            raise ValueError(f"operador unário não permitido: {op_type.__name__}")
        operand = eval_ast(node.operand)
        return ALLOWED_UNARY_OPERATORS[op_type](operand)
    else:
        raise ValueError(f"nó não permitido: {type(node).__name__}")


def safe_calc(expr):
    expr = expr.strip()

    if len(expr) > 50:
        return "erro: expressão muito longa"

    try:
        tree = ast.parse(expr, mode="eval")
        result = eval_ast(tree)
        return f"resultado: {result}"
    except ZeroDivisionError:
        return "erro: divisão por zero"
    except SyntaxError:
        return "erro: sintaxe inválida"
    except ValueError as e:
        return f"erro: {e}"
    except Exception:
        return "erro: expressão inválida"


def process_command(command, auth_user):
    command = command.strip()
    lower_command = command.lower()

    if lower_command == "ping":
        return "pong"

    if lower_command == "status":
        return f"Servidor online | {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"

    if lower_command == "me":
        return f"usuário autenticado: {auth_user['email']} | id: {auth_user['user_id']}"

    if lower_command.startswith("calc "):
        expr = command[5:]
        return safe_calc(expr)

    if lower_command == "exit":
        return "conexao encerrada"

    return "comando invalido"


def handle_client(conn, addr):
    client_ip, client_port = addr
    thread_name = threading.current_thread().name

    logging.info(f"[{thread_name}] conexão recebida de {client_ip}:{client_port}")
    conn.settimeout(CLIENT_TIMEOUT)

    with conn:
        conn_file = conn.makefile("r", encoding="utf-8", newline="\n")
        auth_user = None

        try:
            logging.info(f"[{thread_name}] aguardando auth de {client_ip}")

            auth_message = conn_file.readline()
            if not auth_message:
                logging.warning(f"[{thread_name}] {client_ip} não enviou dados de autenticação")
                conn.sendall(b"auth_fail: sem dados\n")
                return

            auth_message = auth_message.strip()
            logging.info(f"[{thread_name}] auth_message decodificado: {auth_message!r}")

            if not auth_message.startswith("auth "):
                logging.warning(f"[{thread_name}] formato auth inválido de {client_ip}: {auth_message!r}")
                conn.sendall(b"auth_fail: formato invalido\n")
                return

            token = auth_message[5:].strip()
            logging.info(f"[{thread_name}] token recebido? {bool(token)} | tamanho={len(token)}")

            is_valid, result = validate_token(token)
            logging.info(f"[{thread_name}] resultado validate_token: is_valid={is_valid} | result={result!r}")

            if not is_valid:
                msg = f"auth_fail: {result}"
                conn.sendall((msg + "\n").encode("utf-8"))
                logging.warning(f"[{thread_name}] autenticação falhou para {client_ip}: {result}")
                return

            auth_user = result
            conn.sendall(b"auth_ok\n")
            logging.info(
                f"[{thread_name}] autenticação OK para {client_ip} | "
                f"user_id={auth_user['user_id']} | email={auth_user['email']}"
            )

        except Exception as e:
            logging.exception(f"[{thread_name}] erro no handshake auth com {client_ip}: {e}")
            try:
                conn.sendall(f"auth_fail: erro interno - {e}\n".encode("utf-8"))
            except Exception:
                pass
            return

        while True:
            try:
                message = conn_file.readline()
                if not message:
                    logging.info(f"[{thread_name}] conexão encerrada por {client_ip}")
                    break

                message = message.strip()
                if not message:
                    continue

                logging.info(
                    f"[{thread_name}] comando recebido de {client_ip} | "
                    f"user_id={auth_user['user_id']} | email={auth_user['email']} | comando={message!r}"
                )

                response = process_command(message, auth_user)
                conn.sendall((response + "\n").encode("utf-8"))
                save_to_supabase(message, response, client_ip, auth_user)

                if message.lower() == "exit":
                    logging.info(f"[{thread_name}] cliente {client_ip} solicitou encerramento")
                    break

            except socket.timeout:
                logging.warning(f"[{thread_name}] timeout com cliente {client_ip}")
                break
            except Exception as e:
                logging.exception(f"[{thread_name}] erro processando comando de {client_ip}: {e}")
                try:
                    conn.sendall(f"erro: {e}\n".encode("utf-8"))
                except Exception:
                    pass
                break


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"Servidor ouvindo em {HOST}:{PORT}")
    logging.info(f"Servidor iniciado em {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server_socket.accept()

            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            )
            client_thread.start()

            logging.info(
                f"Thread iniciada para {addr} | ativas={threading.active_count() - 1}"
            )

    except KeyboardInterrupt:
        print("\nServidor encerrado manualmente.")
        logging.info("Servidor encerrado manualmente.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()