"environments"


# default settings:

proxy = None

maxsizeinmb = 128

excludedcats = [
    "arthropod",
    "bird",
    "people.p",
    "amphibian",
    "reptile",
    "animals.o",
    "fungi",
    "lifeforms.o",
]


# overwrite them here:

proxy = None
# examples: "socks5://127.0.0.1:1080", "http://127.0.0.1:1079"
# more infomation: https://requests.readthedocs.io/en/latest/user/advanced/#proxies

maxsizeinmb = 128

excludedcats = [
    "arthropod",
    "bird",
    "people.p",
    "amphibian",
    "reptile",
    "animals.o",
    "fungi",
    "lifeforms.o",
]
# valid entries:
# "arthropod", "bird", "amphibian", "fish", "reptile", "shell", "plant", "fungi"
# "animals.o" for other animals, "bone.f" for bones and fossils, "lifeforms.o" for other lifeforms
# "people.p" for reducing portraits of people on portrait, that is, non-landscape monitors
# more infomation: https://commons.wikimedia.org/wiki/Commons:Featured_pictures
