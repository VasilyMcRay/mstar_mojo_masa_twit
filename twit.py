from itertools import cycle
import asyncio
from pathlib import Path

import curl_cffi
from better_proxy import Proxy
import twitter

TWITTERS_TXT = Path("twitters.txt")
PROXIES_TXT = Path("proxies.txt")
RESULTS_TXT = Path("results.txt")
MSTAR_MESSAGES_TXT = Path("mstar_messages.txt")
MOJO_MESSAGES_TXT = Path("mojo_messages.txt")
MASA_MESSAGES_TXT = Path("masa_messages.txt")

for filepath in (
    TWITTERS_TXT,
    PROXIES_TXT,
    RESULTS_TXT,
    MSTAR_MESSAGES_TXT,
    MOJO_MESSAGES_TXT,
    MASA_MESSAGES_TXT,
):
    filepath.touch(exist_ok=True)


TWITTER_ACCOUNTS = twitter.account.load_accounts_from_file(TWITTERS_TXT)
PROXIES = Proxy.from_file(PROXIES_TXT)

if not PROXIES:
    PROXIES = [None]

QUOT_MSTAR_TWEET_URL = "https://twitter.com/Bybit_Official/status/1780504356971774070"
QUOT_MOJO_TWEET_URL = "https://twitter.com/Bybit_Official/status/1780506488701624699"
QUOT_MASA_TWEET_URL = "https://twitter.com/Bybit_Official/status/1780620993087652301"
USER_IDS_TO_FOLLOW = [
    999947328621395968,   # https://twitter.com/Bybit_Official
    1463490378728837125,  # https://twitter.com/weareplanetmojo
    1501667328714547208,  # https://twitter.com/Merlin_Starter
]


async def main():
    proxy_to_account_list = list(zip(cycle(PROXIES), TWITTER_ACCOUNTS))

    for (
        (proxy, twitter_account),
        mstar_quote_message_text,
        mojo_quote_message_text,
        masa_quote_message_text,
    ) in zip(
        proxy_to_account_list,
        open(MSTAR_MESSAGES_TXT, "r").readlines(),
        open(MOJO_MESSAGES_TXT, "r").readlines(),
        open(MASA_MESSAGES_TXT, "r").readlines(),

    ):  # type: (Proxy, twitter.Account), str, str, Path,
        async with twitter.Client(twitter_account, proxy=proxy) as twitter_client:
            try:
                await twitter_client.request_user()

                # Подписка
                for user_id in USER_IDS_TO_FOLLOW:
                    await twitter_client.follow(user_id)
                    print(f"{twitter_account} Подписался на {user_id}")
                    await asyncio.sleep(3)

                # Твит MSTAR
                mstar_tweet = await twitter_client.quote(
                    QUOT_MSTAR_TWEET_URL, mstar_quote_message_text
                )
                print(f"{twitter_account} Сделал Quote твит (MSTAR): {mstar_tweet.url}")
                print(f"\tТекст: {mstar_tweet.text}")
                await asyncio.sleep(3)

                mojo_tweet = await twitter_client.quote(
                    QUOT_MOJO_TWEET_URL, mojo_quote_message_text
                )
                print(f"{twitter_account} Сделал Quote твит (MOJO): {mojo_tweet.url}")
                print(f"\tТекст: {mojo_tweet.text}")
                await asyncio.sleep(3)

                masa_tweet = await twitter_client.quote(
                    QUOT_MASA_TWEET_URL, masa_quote_message_text
                )
                print(f"{twitter_account} Сделал Quote твит (MASA): {masa_tweet.url}")
                print(f"\tТекст: {masa_tweet.text}")
                await asyncio.sleep(3)

                with open(RESULTS_TXT, "a") as results_file:
                    results_file.write(
                        f"{twitter_account.auth_token}, MSTAR: {mstar_tweet.url}, MOJO: {mojo_tweet.url}, MASA: {masa_tweet.url}\n"
                    )

            except curl_cffi.requests.errors.RequestsError as exc:
                print(f"Ошибка запроса. Возможно, плохой прокси: {exc}")
                continue
            except Exception as exc:
                print(f"Что-то очень плохое: {exc}")
                continue

if __name__ == "__main__":
    asyncio.run(main())
