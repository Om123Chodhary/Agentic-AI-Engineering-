from tools import (
    search_web,
    read_webpage
)


results = search_web(
    "South Africa VS Australia cricket match how much score temba bavuma in current series test in 2nd Test Match ",
    max_results=3
)

print("\nSEARCH RESULTS\n")

for result in results:
    print(result["title"])
    print(result["url"])
    print(result["snippet"])
    print()


if results:

    text = read_webpage(
        results[0]["url"]
    )

    print("\nWEBPAGE TEXT\n")
    print(text[:2000])
