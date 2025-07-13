import fastapi
from fastapi import Query
import requests as req
import re
from bs4 import BeautifulSoup
import json
import py_mini_racer

app = fastapi.FastAPI(
    title="Piclean API", description="An awesome API for Picrew", version="0.1.0"
)
site = "https://picrew.me/"
api = "https://api.picrew.me/"
cdn = "https://cdn.picrew.me/"


@app.get("/", description="Just gives some info to people stumbling upon it")
def root():
    return {
        "message": "Piclean API",
        "version": "0.1.0",
        "documentation": ["/docs", "/redoc"],
        "repo": "https://github.com/sebastian-92/piclean-api",
    }


@app.get("/discovery")  # discovery page
def discovery(
    lang: str = Query(
        default="en", title="Language", description="Two character language code"
    ),
    page: int = Query(
        default=1, title="Page Number", description="Page number for pagination"
    ),
    per_page: int = Query(
        default=40,
        title="Items per Page",
        description="Number of items to return per page",
        le=48,
        ge=1,
    ),
):
    res = req.get(
        api + f"player/api/discovery?per_page={per_page}&page={page}&lang={lang}"
    )  # discover is the only thing that uses the internal picrew api for some reason
    data = res.json()
    content = []
    for i in data:
        content.append(
            {
                "id": i["id"],
                "thumb": i["url"],
                "canvas_size": i["cs"],
            }
        )
    return content


@app.get("/search")  # search page
def search(
    q=Query(
        default="",
        title="Search Query",
        description="Search query for Picrew images",
    ),
    page=Query(
        default=1, title="Page Number", description="Page number for pagination"
    ),
    licenses=Query(
        default="1111",
        description="license expressed as four boolean bits in this order: personal, commercial, noncommercial, and processing",
        openapi_examples={
            "1111": {"value": "1111", "summary": "All licenses"},
            "1000": {"value": "1000", "summary": "Personal use only"},
            "0100": {"value": "0100", "summary": "Commercial use only"},
            "0011": {
                "value": "0011",
                "summary": "Both Processing and Non-Commercial allowed",
            },
        },
    ),
    cs=Query(
        default="",
        title="Canvas Size",
        description="filters by canvas size",
        openapi_examples={
            "1:1": {"value": 1, "summary": "1:1 canvas size"},
            "9:16": {"value": 100, "summary": "9:16 canvas size"},
        },
    ),
    imt=Query(
        default=1,
        title="Image Maker Type",
        description="filters by type 1 for dress up, 2 for random",
        openapi_examples={
            "1": {"value": 1, "summary": "Dress up type"},
            "2": {"value": 2, "summary": "Random type"},
        },
    ),
    sort=Query(
        default=2,
        title="Sort Order",
        description="Order to sort image makers by",
        openapi_examples={
            "1": {"value": 1, "summary": "Recently updated"},
            "2": {"value": 2, "summary": "Hot now"},
        },
    ),
    type=Query(
        default=3,
        title="Search Type",
        description="Change what type of search to do",
        openapi_examples={
            "1": {"value": 1, "summary": "Tags: Fuzzy"},
            "2": {"value": 2, "summary": "Tags: Exact"},
            "3": {"value": 3, "summary": "Full Text"},
        },
    ),
    lang=Query(
        default="en", title="Language Code", description="Two character language code"
    ),
):
    response = req.get(
        site
        + f"{lang}/search?qt={q}&page={page}&c={licenses}&cs={cs}&imt={imt}&s={sort}&type={type}"
    )
    print(f"Request URL: {response.url}")  # Debugging line to check the request URL
    # Add return statement and error handling
    if response.status_code == 200:
        soop = BeautifulSoup(response.text, "html.parser")
        print(soop.prettify())  # Debugging line to check the HTML structure
        creators = soop.find_all(class_="search-ImagemakerList_Creator")
        images = soop.find_all(class_="search-ImagemakerList_Icon")
        titles = soop.find_all(class_="search-ImagemakerList_Title")
        ids = re.findall(r"image_maker/([0-9]+)", soop.prettify())[::3]
        print(
            f"Found {len(creators)} creators, {len(images)} images, {len(titles)} titles, and {len(ids)} ids"
        )
        results = []
        for i in range(len(creators)):
            print(f"Processing creator {i + 1}/{len(creators)}")
            results.append(
                {
                    "id": ids[i],
                    "creator": creators[i].get_text().strip(),
                    "image": images[i].get("data-bg").strip(),
                    "title": titles[i].get_text().strip(),
                }
            )
        return {
            "results": results,
            "page": page,
        }
    else:
        return {"error": "Failed to fetch search results"}


@app.get("/idata/{id}")  # image maker page
def getData(
    id: int,
    lang: str = Query(
        default="en", title="Language", description="Two character language code"
    ),
):
    response = req.get(site + f"{lang}/image_maker/{id}")
    if response.status_code == 200:
        data = response.text
        js = re.findall(
            r"<script>window\.__NUXT__=(.+);</script><script crossorigin=\"anonymous\"",
            data,
        )
        # pythonmonkey has a fricking bug where it doesn't like to work in flask or fastapi
        # py_mini_racer to the rescue
        ctx = py_mini_racer.MiniRacer()
        ctx.eval("nuxt =" + js[0]) if js else None
        # credit to this reddit thread for knowing where to find the data https://www.reddit.com/r/picrew/comments/1bh6jgq
        info = json.loads(ctx.eval("JSON.stringify(nuxt.state.imageMakerInfo)"))
        cf = json.loads(ctx.eval("JSON.stringify(nuxt.state.config)"))
        img = json.loads(ctx.eval("JSON.stringify(nuxt.state.commonImages)"))
        i_rule = json.loads(ctx.eval("JSON.stringify(nuxt.state.itemRule)"))
        scales = json.loads(ctx.eval("JSON.stringify(nuxt.state.scales)"))
        return {
            "id": id,
            "imageMakerInfo": info,
            "config": cf,
            "commonImages": img,
            "itemRule": i_rule,
            "scales": scales,
        }
    else:
        return {
            "error": "Failed to fetch data from Picrew (status code: {})".format(
                response.status_code
            )
        }
