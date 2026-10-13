def publish_reviewed(client, path, **kwargs):
    read = client.get(path.removesuffix('/publish'), headers=kwargs.get('headers'))
    assert read.status_code == 200, read.text
    return client.post(path, json={'expected_revision': read.json()['revision']}, **kwargs)
