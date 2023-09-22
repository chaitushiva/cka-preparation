import requests

def get_alpine_tags():
    url = "https://registry.hub.docker.com/v2/repositories/library/alpine/tags/"
    response = requests.get(url)

    if response.status_code == 200:
        tags_data = response.json()
        return [tag['name'] for tag in tags_data]

    print(f"Failed to retrieve tags. Status code: {response.status_code}")
    return []

if __name__ == "__main__":
    alpine_tags = get_alpine_tags()
    print("Tags for Alpine image:")
    for tag in alpine_tags:
        print(tag)
