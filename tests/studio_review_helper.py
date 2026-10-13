def publish_reviewed(client, path, **kwargs):
    read = client.get(path.removesuffix('/publish'), headers=kwargs.get('headers'))
    assert read.status_code == 200, read.text
    if read.json()['status'] == 'draft':
        read = client.post(path.removesuffix('/publish')+'/submit-review', json={'expected_revision': read.json()['revision']}, **kwargs)
        assert read.status_code == 200, read.text
    return client.post(path, json={'expected_revision': read.json()['revision']}, **kwargs)
