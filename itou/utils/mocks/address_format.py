import random

from itou.asp.models import Commune
from itou.utils.apis.exceptions import AddressLookupError


# https://api-adresse.data.gouv.fr/search/?q=42+Rue+du+clos+de+la+Grange%2C+58160+Sauvigny-les-Bois&limit=1
BAN_GEOCODING_API_RESULTS_FOR_SNAPSHOT_MOCK = {
    "score": 0.8107390909090908,
    "address_line_1": "Rue du Clos de la Grange",
    "number": "42",
    "lane": "Rue du Clos de la Grange",
    "address": "Rue du Clos de la Grange",
    "post_code": "58160",
    "insee_code": "58273",
    "city": "Sauvigny-les-Bois",
    "longitude": 3.271964,
    "latitude": 46.966611,
}

BAN_GEOCODING_API_RESULTS_MOCK = [
    {
        "score": 0.8745736363636364,
        "ban_api_resolved_address": "37 B Rue du Général De Gaulle, 67118 Geispolsheim",
        "address_line_1": "37 B Rue du Général De Gaulle",
        "number": "37b",
        "lane": "Rue du Général de Gaulle",
        "address": "37 b Rue du Général de Gaulle",
        "post_code": "67118",
        "insee_code": "67152",
        "city": "Geispolsheim",
        "longitude": 7.644817,
        "latitude": 48.515883,
    },
    {
        "score": 0.8533299999999999,
        "address_line_1": "382 ROUTE DE JOLLIVET",
        "number": "382",
        "lane": "Route de Jollivet",
        "address": "382 Route de Jollivet",
        "post_code": "07200",
        "insee_code": "07141",
        "city": "Lentillères",
        "longitude": 4.318977,
        "latitude": 44.61615,
    },
    {
        "score": 0.6782018181818182,
        "address_line_1": "5 rue La Maraîchère",
        "number": "5",
        "lane": "rue La Maraichere",
        "address": "5 La Maraichere",
        "post_code": "08440",
        "insee_code": "08488",
        "city": "Vivier-au-Court",
        "longitude": 4.818209,
        "latitude": 49.732732,
    },
    {
        "score": 0.51601979020979,
        "address_line_1": "35 AVENUE DES PERDRIX BOT",
        "number": "35",
        "lane": "Avenue des Perdrix",
        "address": "35 Avenue des Perdrix",
        "post_code": "12850",
        "insee_code": "12176",
        "city": "Onet-le-Château",
        "longitude": 2.571139,
        "latitude": 44.379806,
    },
    {
        "score": 0.8872845454545454,
        "address_line_1": "67 boulevard la fontaine",
        "number": "67",
        "lane": "Boulevard la Fontaine",
        "address": "67 Boulevard la Fontaine",
        "post_code": "67200",
        "insee_code": "67482",
        "city": "Strasbourg",
        "longitude": 7.705596,
        "latitude": 48.58932,
    },
    {
        "score": 0.8606118181818181,
        "address_line_1": "2 place louise michel",
        "number": "2",
        "lane": "Place Louise Michel",
        "address": "2 Place Louise Michel",
        "post_code": "62280",
        "insee_code": "62758",
        "city": "Saint-Martin-Boulogne",
        "longitude": 1.623944,
        "latitude": 50.737565,
    },
    {
        "score": 0.8688054545454545,
        "address_line_1": "CITE SAINT PAUL",
        "number": None,
        "lane": None,
        "address": "Cite Saint Paul",
        "post_code": "62220",
        "insee_code": "62215",
        "city": "Carvin",
        "longitude": 2.925345,
        "latitude": 50.473074,
    },
    {
        "score": 0.8543018181818182,
        "address_line_1": "261 CHEMIN DES ESCANCES",
        "number": "261",
        "lane": "Chemin des Escances",
        "address": "261 Chemin des Escances",
        "post_code": "83390",
        "insee_code": "83100",
        "city": "Puget-Ville",
        "longitude": 6.150673,
        "latitude": 43.287046,
    },
    {
        "score": 0.4545536363636364,
        "address_line_1": "APPARTEMENT 99 Entree 9 Lieu Dit Bloc les Pinsons",
        "number": None,
        "lane": None,
        "address": "Lieu Dit Bloc les Pinsons",
        "post_code": "62219",
        "insee_code": "62525",
        "city": "Longuenesse",
        "longitude": 2.263412,
        "latitude": 50.741776,
    },
    {
        "score": 0.8654681818181817,
        "address_line_1": "1 passage Jules ferry",
        "number": "1",
        "lane": "Passage Jules Ferry",
        "address": "1 Passage Jules Ferry",
        "post_code": "87350",
        "insee_code": "87114",
        "city": "Panazol",
        "longitude": 1.3094,
        "latitude": 45.82893,
    },
    {
        "score": 0.870890909090909,
        "address_line_1": "2 square Pierre et Marie Curie",
        "number": "2",
        "lane": "Square Pierre et Marie Curie",
        "address": "2 Square Pierre et Marie Curie",
        "post_code": "77100",
        "insee_code": "77284",
        "city": "Meaux",
        "longitude": 2.902674,
        "latitude": 48.948806,
    },
    {
        "score": 0.3168495104895105,
        "address_line_1": "7 hameau de beylesse",
        "number": None,
        "lane": None,
        "address": "Hameau des Vidals",
        "post_code": "83340",
        "insee_code": "83136",
        "city": "Le Thoronet",
        "longitude": 6.329226,
        "latitude": 43.439081,
    },
    {
        "score": 0.8781490909090909,
        "address_line_1": "16 QUARTIER DE LA MAGDELEINE",
        "number": "16",
        "lane": "Quartier de la Magdeleine",
        "address": "16 Quartier de la Magdeleine",
        "post_code": "88000",
        "insee_code": "88160",
        "city": "Épinal",
        "longitude": 6.439808,
        "latitude": 48.18722,
    },
    {
        "score": 0.8662299999999999,
        "address_line_1": "1 RESIDENCE PABLO NERUDA",
        "number": "1",
        "lane": "Residence Pablo Néruda",
        "address": "1 Residence Pablo Néruda",
        "post_code": "62680",
        "insee_code": "62570",
        "city": "Méricourt",
        "longitude": 2.877261,
        "latitude": 50.398305,
    },
    {
        "score": 0.8695790909090908,
        "address_line_1": "172 voie du cheminet",
        "number": "172",
        "lane": "Voie du Cheminet",
        "address": "172 Voie du Cheminet",
        "post_code": "91420",
        "insee_code": "91432",
        "city": "Morangis",
        "longitude": 2.32619,
        "latitude": 48.708599,
    },
    {
        "score": 0.8673690909090909,
        "address_line_1": "3 allée Louis Jouvet",
        "number": "3",
        "lane": "Allée Louis Jouvet",
        "address": "3 Allée Louis Jouvet",
        "post_code": "41100",
        "insee_code": "41269",
        "city": "Vendôme",
        "longitude": 1.062354,
        "latitude": 47.808359,
    },
    {
        "score": 0.8745736363636364,
        "address_line_1": "37 Ter Rue du Général De Gaulle",
        "number": "37t",
        "lane": "Rue du Général de Gaulle",
        "address": "37 t Rue du Général de Gaulle",
        "post_code": "67118",
        "insee_code": "67152",
        "city": "Geispolsheim",
        "longitude": 7.644817,
        "latitude": 48.515883,
    },
    {
        "score": 0.8745736363636364,
        "address_line_1": "37 G Rue du Général De Gaulle",
        "number": "37g",
        "lane": "Rue du Général de Gaulle",
        "address": "37 G Rue du Général de Gaulle",
        "post_code": "67118",
        "insee_code": "67152",
        "city": "Geispolsheim",
        "longitude": 7.644817,
        "latitude": 48.515883,
    },
    {
        "score": 0.405858347107438,
        "address_line_1": "2 allée de la Calypso",
        "number": "2",
        "lane": "Rue de la Vallée aux Loups",
        "address": "2 Rue de la Vallée aux Loups",
        "post_code": "86000",
        "insee_code": "86194",
        "city": "Poitiers",
        "longitude": 0.361979,
        "latitude": 46.57942,
    },
    {
        "score": 0.27856937799043063,
        "address_line_1": "33 LE BOURGOGNE",
        "number": None,
        "lane": None,
        "address": "Residence les Prov Fses Bat Bourgogn",
        "post_code": "59330",
        "insee_code": "59291",
        "city": "Hautmont",
        "longitude": 3.928199,
        "latitude": 50.243995,
    },
    {
        "score": 0.44045145067698255,
        "address_line_1": "résidence INCONNUE 9/93 place 9osette de Mey",
        "number": None,
        "lane": None,
        "address": "Place Rosette de Mey",
        "post_code": "59000",
        "insee_code": "59350",
        "city": "Lille",
        "longitude": 3.025616,
        "latitude": 50.630188,
    },
    {
        "score": 0.16679584415584414,
        "address_line_1": "24 bd de l'espérance",
        "number": None,
        "lane": None,
        "address": "Rue François Arago Saint-pol",
        "post_code": "59430",
        "insee_code": "59183",
        "city": "Dunkerque",
        "longitude": 2.398729,
        "latitude": 51.043103,
    },
    {
        "score": 0.5555026392961877,
        "address_line_1": "CHEZ TARTEMPION 10 r henri gormand 69120 Vaulx-en-Velin",
        "number": "10",
        "lane": "Rue Henri Gormand",
        "address": "10 Rue Henri Gormand",
        "post_code": "69120",
        "insee_code": "69256",
        "city": "Vaulx-en-Velin",
        "longitude": 4.925175,
        "latitude": 45.749174,
    },
    {
        "score": 0.6832486776859503,
        "address_line_1": "8 la boutrie - caillot",
        "number": "8",
        "lane": "la boutrie - caillot",
        "address": "8 la boutrie - caillot",
        "post_code": "85600",
        "insee_code": "85146",
        "city": "Montaigu-Vendée",
        "longitude": -1.297749,
        "latitude": 47.012473,
    },
    BAN_GEOCODING_API_RESULTS_FOR_SNAPSHOT_MOCK,
]

# Revert lookup
RESULTS_BY_BAN_API_RESOLVED_ADDRESS = {}
for elt in BAN_GEOCODING_API_RESULTS_MOCK:
    if "ban_api_resolved_address" in elt:
        RESULTS_BY_BAN_API_RESOLVED_ADDRESS[elt["ban_api_resolved_address"]] = elt


def mock_get_first_geocoding_data(_address, **_):
    return BAN_GEOCODING_API_RESULTS_MOCK[0]


def mock_get_geocoding_data(address, **_):
    for result in BAN_GEOCODING_API_RESULTS_MOCK:
        if address.startswith(result["address_line_1"]):
            return result
    raise AddressLookupError(f"Unable to lookup address: {address}")


def mock_get_geocoding_data_by_ban_api_resolved(address, **_):
    return RESULTS_BY_BAN_API_RESOLVED_ADDRESS.get(address)


def get_random_geocoding_api_result():
    return random.choice(BAN_GEOCODING_API_RESULTS_MOCK)


def get_random_insee_code():
    return get_random_geocoding_api_result()["insee_code"]


def get_random_asp_commune():
    return Commune.objects.by_insee_code(get_random_insee_code())
