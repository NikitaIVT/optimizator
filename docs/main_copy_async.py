"""RabbitMQ"""
import json
import pika
import datetime
import asyncio
from aio_pika import connect_robust, Message
from aio_pika.exceptions import AMQPConnectionError

from docs.database import settings, Serialize

command = "three_month"
start_date = datetime.datetime(2025,1,1)


def str_to_date(start_date):
    """
    Переводит строку в datetime
    """
    if start_date and '.' in start_date:
        start_date = start_date[:start_date.index('.')]
    if start_date and isinstance(start_date, str):
        if 'Z' in start_date:
            start_date = start_date[:-1]
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
    return start_date


async def consume(queue):
    """
    Асинхронный обработчик сообщений RabbitMQ с параллельной обработкой
    """
    async for message in queue:
        # Запускаем независимую задачу для обработки сообщения
        asyncio.create_task(callback(message))


async def publish_message(data, routing_key="krai_out"):
    """
    Публикация сообщения в RabbitMQ.
    """
    try:
        connection = await connect_robust(host=settings.rabbit_mq_host,
                                          login=settings.RMQ_USER.get_secret_value(),
                                          password=settings.RMQ_PASS.get_secret_value())
        async with connection:  # Контекстное управление соединением
            channel = await connection.channel()  # Создаем канал
            # Формируем сообщение
            message = Message(data.encode())
            # Публикуем сообщение без явного обменника (через `routing_key`)
            await channel.default_exchange.publish(
                message,
                routing_key=routing_key,
            )
            print("Сообщение отправлено")
            print("Сообщение отправлено")
    except Exception as e:
        print(f"Ошибка отправки сообщения {e}")
        print(f"Ошибка отправки сообщения {e}")


async def callback(message):
    """
    Главная функция принимающая в себя сообщения из кролика и вызывающая соответствующие функции микросервиса
    """
    global command
    global start_date

    from docs.optimizer import three_month_start

    body = message.body.decode('utf-8')
    data = json.loads(body)  # Разбираем JSON
    command = data.get('requests')
    print(command)
    print(command)
    msg_out = ''

    match Serialize.get_command(command):
        case "Трехмесячный оптимизатор":
            start_data = data.get("start_data")
            plan_id = data.get("digital_twin")
            await asyncio.to_thread(three_month_start, start_data, plan_id)
            print("очистка")
            print("очистка")
        case _:
            print("Неправильное сообщение")
            print("Неправильное сообщение")

    # Комбинируем параметры в словарь
    message_params = {
        'msg_out': msg_out
    }

    # Сериализуем словарь в строку JSON
    msg_out = json.dumps(message_params)

    # Отправляем сообщение в очередь
    await publish_message(msg_out)


async def main():
    try:
        connection = await connect_robust(host=settings.rabbit_mq_host,
                                          login=settings.RMQ_USER.get_secret_value(),
                                          password=settings.RMQ_PASS.get_secret_value())
        async with connection:
            channel = await connection.channel()

            queue = await channel.declare_queue('krai_requests', durable=True)
            await channel.declare_queue('krai_out', durable=True)

            print('Waiting for messages from the "krai_requests" queue. Press CTRL+C to exit')
            print('Waiting for messages from the "krai_requests" queue. Press CTRL+C to exit')

            await consume(queue)


    except pika.exceptions.AMQPConnectionError as e:
        print(f'Connection error: {e}')


# asyncio.run(main())
