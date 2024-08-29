from dataclasses import asdict
import math
from typing import List, Union
from fastapi import FastAPI, HTTPException, Path
from core.models import Pokemon

list_pokemons = {}

app = FastAPI(
    title="Test",
    description="Test API",
    version="0.1.0",
)


#===========================GET============================
@app.get("/total_pokemons")
def get_total_pokemons() -> dict:
    return {"total": len(list_pokemons)}

@app.get("/pokemons")
def get_all_pokemons1() -> List[Pokemon]:
    res = [Pokemon(**list_pokemons[id]) for id in list_pokemons]
    return res

@app.get("/pokemon/{id}")
def get_pokemon_by_id(id: int = Path(ge=1)) -> Pokemon:
    if id not in list_pokemons:
        raise HTTPException(status_code=404, detail="Ce pokemon n'existe pas")
    return Pokemon(**list_pokemons[id])

#===========================POST============================
@app.post("/pokemon/")
def create_pokemon(pokemon: Pokemon) -> Pokemon:
    if pokemon.id in list_pokemons:
        raise HTTPException(status_code=400, detail=f"Le pokemon {pokemon.id} existe déjà !")
    list_pokemons[pokemon.id] = asdict(pokemon)
    return pokemon

#===========================PUT============================
@app.put("/pokemon/{id}")
def update_pokemon(id: int, pokemon: Pokemon) -> Pokemon:
    if id not in list_pokemons:
        raise HTTPException(status_code=404, detail=f"Le pokemon {id} n'existe pas.")
    list_pokemons[id] = asdict(pokemon)
    return pokemon

#===========================DELETE============================
@app.delete("/pokemon/{id}")
def delete_pokemon(id: int = Path(ge=1)) -> Pokemon:
    if id in list_pokemons:
        pokemon = Pokemon(**list_pokemons[id])
        del list_pokemons[id]
        return pokemon
    raise HTTPException(status_code=404, detail=f"Le pokemon {id} n'existe pas.")

#===========================GET============================
@app.get("/types")
def get_all_types() -> List[str]:
    types = []
    for pokemon in list_pokemons.values():
        for type in pokemon["types"]:
            if type not in types:
                types.append(type)
    types.sort()
    return types

@app.get("/pokemons/search/")
def search_pokemons(
    types: Union[str, None] = None,
    evo: Union[str, None] = None,
    totalgt: Union[int, None] = None,
    totallt: Union[int, None] = None,
    sortby: Union[str, None] = None,
    order: Union[str, None] = None,
) -> Union[List[Pokemon], None]:
    
    filtered_list = []
    res = []

    # Filter by types
    if types is not None:
        for pokemon in list_pokemons.values():
            if set(types.split(",")).issubset(pokemon["types"]):
                filtered_list.append(pokemon)

    # Filter by evolution
    if evo is not None:
        tmp = filtered_list if filtered_list else list_pokemons.values()
        new = [pokemon for pokemon in tmp if (evo == "true" and "evolution_id" in pokemon) or (evo == "false" and "evolution_id" not in pokemon)]
        filtered_list = new

    # Filter by greater than total
    if totalgt is not None:
        tmp = filtered_list if filtered_list else list_pokemons.values()
        new = [pokemon for pokemon in tmp if pokemon["total"] > totalgt]
        filtered_list = new

    # Filter by less than total
    if totallt is not None:
        tmp = filtered_list if filtered_list else list_pokemons.values()
        new = [pokemon for pokemon in tmp if pokemon["total"] < totallt]
        filtered_list = new

    # Sort results
    if sortby is not None and sortby in ["id", "name", "total"]:
        filtered_list = filtered_list if filtered_list else list_pokemons.values()
        sorting_order = False if order == "asc" else True
        filtered_list = sorted(filtered_list, key=lambda d: d[sortby], reverse=sorting_order)

    # Response
    if filtered_list:
        res = [Pokemon(**pokemon) for pokemon in filtered_list]
        return res
    
    raise HTTPException(status_code=404, detail="Aucun Pokemon ne répond aux critères de recherche")

#=====Tous les Pokémons avec la pagination=====
@app.get("/pokemons2/")
def get_all_pokemons(page: int = 1, items: int = 10) -> List[Pokemon]:
    items = min(items, 20)
    max_page = math.ceil(len(list_pokemons) / items)
    current_page = min(page, max_page)
    start = (current_page - 1) * items
    stop = start + items if start + items <= len(list_pokemons) else len(list_pokemons)
    sublist = list(list_pokemons.keys())[start:stop]

    res = [Pokemon(**list_pokemons[id]) for id in sublist]
    
    return res
