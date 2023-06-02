"functions"
import env
import math, re, requests, sys, tqdm


def get(url, filepath=None, stream=False, proxy=env.proxy):
    "returns an exception name (string) instead of a requests.models.Response if an error occurs"
    dict = None
    if proxy:
        dict = {"http": proxy, "https": proxy}
    try:
        r = requests.get(
            url,
            proxies=dict,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
            stream=filepath and stream,
        )
    except:
        r = type(sys.exception()).__name__
    if filepath:
        with open(filepath, "wb") as f:
            if stream:
                sizeinkb = math.ceil(int(r.headers["content-length"]) / 1024)
                with tqdm.tqdm(
                    total=sizeinkb, desc="downloading", unit="kb", postfix=filepath
                ) as probar:
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)
                        probar.update(1)
            else:
                f.write(r.content)
    return r


def calcat(usages):
    "input a url list"
    cat = 0
    for usage in usages:
        usage = usage.lower()
        if "/arthropod" in usage:
            cat |= 1 << 0
        if "/bird" in usage:
            cat |= 1 << 1
        if "/people" in usage:
            cat |= 1 << 2
        if "/amphibian" in usage:
            cat |= 1 << 3
        if "/fish" in usage:
            cat |= 1 << 4
        if "/reptile" in usage:
            cat |= 1 << 5
        if re.search("/animals[^/]", usage):
            cat |= 1 << 6
        if "/bone" in usage:
            cat |= 1 << 7
        if "/shell" in usage:
            cat |= 1 << 8
        if "/plant" in usage:
            cat |= 1 << 9
        if "/fungi" in usage:
            cat |= 1 << 10
        if "lifeforms" in usage:
            cat |= 1 << 11
    return cat


def path(dir, filename):
    "combine a dir and a filename into a path"
    if dir:
        return f"{dir}/{filename}"
    else:
        return filename
