import argparse
from typing import Dict, Optional
from telethon import TelegramClient
from datetime import date, datetime
import json
from collections import defaultdict


CREDENTIALS_FILE = "credentials.json"

HTML_TEMPLATE_HEADER = """
<html>

<head>
    <title>T Messages</title>
    <script src="https://cdn.canvasjs.com/ga/canvasjs.min.js"></script>
    <script>
        window.onload = function () {
            var chart = new CanvasJS.Chart("chartContainer", {
                theme: "light2", // "light1", "dark1", "dark2"
                animationEnabled: true,
                zoomEnabled: true,
                title: {
                    text: "T Messages"
                },
                data: [{
                    type: "area",
                    xValueType: "dateTime",
                    dataPoints:
                    """
HTML_TEMPLATE_FOOTER = """
            }]
        });
        chart.render();
    }
    </script>
</head>

<body>
    <div id="chartContainer" style="width: 100%; height: 400px;"></div>
</body>
"""


async def get_message_chart(
    client: TelegramClient, username: str, start_dt: Optional[date] = None
) -> Dict[date, int]:
    res = defaultdict(int)
    async for msg in client.iter_messages(username):
        if start_dt and msg.date.date() < start_dt.date():
            break
        res[str(msg.date.date())] += 1
    res = list(res.items())
    res.sort(key=lambda x: x[0])
    return res


def load_all_messages(username: str):
    with open(CREDENTIALS_FILE, "r") as credentials_fd:
        credentials = json.load(credentials_fd)
    with TelegramClient(
        "user", credentials["api_id"], credentials["api_hash"]
    ) as client:
        return client.loop.run_until_complete(get_message_chart(client, username))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a message chart for a Telegram user."
    )
    parser.add_argument(
        "username", type=str, help="The Telegram username to fetch messages for."
    )
    args = parser.parse_args()
    messages = load_all_messages(args.username)
    messages = [
        {"x": datetime.strptime(k, "%Y-%m-%d").timestamp() * 1000, "y": v}
        for k, v in messages
    ]

    with open("chart.html", "w") as chart_fd:
        chart_fd.write(HTML_TEMPLATE_HEADER)
        chart_fd.write(json.dumps(messages))
        chart_fd.write(HTML_TEMPLATE_FOOTER)

    return 0
