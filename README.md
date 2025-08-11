# ctext.org_-crawler

A minimal crawler for [ctext.org](https://ctext.org/) using its API.

```bash
python crawler.py --output texts --delay 1.0 --root zhs
```

The script recursively retrieves entries starting from the given root node
(`zhs` for Chinese) and writes each text to a file under the specified
output directory.
