def scale_ingredients(milk_amount_liters, original_ingredients):
    """
    Scale the ingredients based on the amount of milk used and express them as combinations
    of the allowed teaspoon measurements (1/2, 1/4, ..., 1/128), and include the remainder
    in units of 1/256 teaspoon.

    :param milk_amount_liters: The amount of milk in liters.
    :param original_ingredients: A dictionary of original ingredients and their amounts (in teaspoons).
    :return: A dictionary of scaled ingredients expressed as combinations of teaspoon measurements,
             along with the remainder in 1/256 tsp units.
    """
    # Define the set of teaspoon measurements in descending order
    teaspoon_measurements = [1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128]

    scaled_ingredients = {}
    for ingredient, amount in original_ingredients.items():
        if ingredient=='name' or ingredient=='milk' or ingredient=='html' or ingredient=='receta':
            continue
        # Scale the ingredient amount
        scaled_amount = amount * milk_amount_liters / original_ingredients["milk"]

        # Break down the scaled amount into combinations of teaspoon measurements
        remaining_amount = scaled_amount
        combination = []
        for measurement in teaspoon_measurements:
            if remaining_amount >= measurement:
                count = int(remaining_amount // measurement)
                # Convert the measurement to a fraction string
                if measurement == 1/2:
                    fraction = "1/2"
                elif measurement == 1/4:
                    fraction = "1/4"
                elif measurement == 1/8:
                    fraction = "1/8"
                elif measurement == 1/16:
                    fraction = "1/16"
                elif measurement == 1/32:
                    fraction = "1/32"
                elif measurement == 1/64:
                    fraction = "1/64"
                elif measurement == 1/128:
                    fraction = "1/128"
                combination.append(f"{count} x {fraction} tsp")
                remaining_amount -= count * measurement

        # Calculate the remainder in units of 1/256 teaspoon
        remainder_256 = remaining_amount / (1/256)

        # Store the combination and remainder as a string
        scaled_ingredients[ingredient] = {
            "combination": " + ".join(combination) if combination else "0 tsp",
            "remainder_256": remainder_256
        }

    return scaled_ingredients


####################################################################################
####################################################################################

# Example usage
# original_ingredients = {
#     "name":"Camembert",  # vaca o cabra
#     "milk":10, # Litros de leche
#     "mesophilic": 1/4+1/16,   # 1/2 tsp
#     "Pen. C.": 1/8+1/32,      # 1/4 tsp
#     "Geo. C.": 1/16+1/64,     # 1/8 tsp
#     "Rennet": 1/2,            # 1/16 tsp
#     "CaCl": 1/4+1/8,          # 1/32 tsp
# }

original_ingredients = {
    "html":"https://cheesemaking.com/products/alpine-tomme-recipe",
    "name":"Alpine Tomme",  # vaca o cabra
    "milk":8, # Litros de leche
#    "mesophilic": 1/16,        # 1/2 tsp
    "thermophilic": 1/4,        # 1/2 tsp
    "Rennet":  1/4+1/8,            # 1/16 tsp
    "CaCl":    1/2,            # 1/32 tsp
}


BlueCastle = {
    "datos":{
        "html":"https://www.youtube.com/watch?v=a_PeXcz4W8A&t=1064s",
        "name":"Castle Blue",  # vaca
        "receta": """
        1- Calentar leche a 32°C
        2- Agregar cultivos, esperar 5m, revolver
        3- Dejar madurar por 90min
        4- Agregar CaCl y Rennet
        5- Esperar 4 veces el tiempo de floculacion (tapa liviana no rota encima)
        6- Cortar cuajo y esperar 5 min
        7- Revolver cuajo por 30min
        8- Sacar suero y poner en moldes con el espumador
        9- Drenar por 2 horas
        10- Darlos vuelta y dejar tada la noche
        11- Darlos vuelta y dejar por 2 horas
        12- Salar quesos individuales
        13- A la caja de maduracion por 1 semana
        14- Perforar a los 10 dias
        """},

    "ingredients":{
        "milk":6.5,# Litros de leche "Penicil. Roq.": 1/8, # 1/4 queso diluido en leche
        "mesophilic": 1/8, # 1/2 tsp
        "Rennet": 1/4, # 1/16 tsp
        "CaCl": 1/4, # 1/32 tsp
        
    }
}



original_ingredients = {
    "html":"https://www.youtube.com/watch?v=a_PeXcz4W8A&t=1064s",
    "name":"Castle Blue",  # vaca
    "receta": """
    1- Calentar leche a 32°C
    2- Agregar cultivos, esperar 5m, revolver
    3- Dejar madurar por 90min
    4- Agregar CaCl y Rennet
    5- Esperar 4 veces el tiempo de floculacion (tapa liviana no rota encima)
    6- Cortar cuajo y esperar 5 min
    7- Revolver cuajo por 30min
    8- Sacar suero y poner en moldes con el espumador
    9- Drenar por 2 horas
    10- Darlos vuelta y dejar tada la noche
    11- Darlos vuelta y dejar por 2 horas
    12- Salar quesos individuales
    13- A la caja de maduracion por 1 semana
    14- Perforar a los 10 dias
    """,
    "milk":6.5, # Litros de leche "Penicil. Roq.": 1/8, # 1/4 queso diluido en leche
    "mesophilic": 1/8, # 1/2 tsp
    "Rennet": 1/4, # 1/16 tsp
    "CaCl": 1/4, # 1/32 tsp
}


# original_ingredients = {
#     "name":"Manchego",  # vaca o cabra
#     "milk":8, # Litros de leche
#     "mesophilic": 1/16,        # 1/2 tsp
#     "thermophilic": 1/16,        # 1/2 tsp
    
#     #    "Pen. C.": 1/8+1/32,      # 1/4 tsp
# #    "Geo. C.": 1/16+1/64,     # 1/8 tsp
#     "Rennet":  1/2,            # 1/16 tsp
#     "CaCl":    1,            # 1/32 tsp
# }

# original_ingredients = {
#     "name":"DoubleGloucester",  # vaca o cabra
#     "milk":12, # Litros de leche
#     "mesophilic": 3/8,        # 1/2 tsp
# #    "Pen. C.": 1/8+1/32,      # 1/4 tsp
# #    "Geo. C.": 1/16+1/64,     # 1/8 tsp
#     "Rennet":  3/4,            # 1/16 tsp
#     "CaCl":    3/4,            # 1/32 tsp
# }

# original_ingredients = {
#     "name":"Valencay", #  cabra
#     "milk":8, # Litros de leche
#     "mesophilic": 1/8,   # 1/2 tsp
#     "Pen. C.": 1/16,      # 1/4 tsp
#     "Geo. C.": 1/64,     # 1/8 tsp
#     "Rennet": 1/4+1/8,            # 1/16 tsp
#     "CaCl": 1/2,          # 1/32 tsp
# }

# original_ingredients = {
#     "name":"Valencay 2",  #  cabra
#     "milk": 4           , # Litros en la receta
#     "mesophilic": 1/4,    #  tsp
#     "Pen. C.": 1/8,      #  tsp
#     "Geo. C.": 1/64,      #  tsp
#     "Rennet": 1/4,    #  tsp
#     "CaCl": 1/4,          #  tsp
# }


queso=BlueCastle
# Amount of milk you want to use (in liters)
milk_amount_liters = 8  # Example: 2.5 liters of milk

# Scale the ingredients
scaled_ingredients = scale_ingredients(milk_amount_liters, original_ingredients)

# Print the scaled ingredients in a well-tabulated format
print("-" * 100)
print("Receta para {} litros de leche de queso \"{}\"".format(milk_amount_liters,original_ingredients["name"]))
print("-" * 100)
print("{:<15} {:<60} {:<20}".format("Ingredient", "Scaled Amount", "Remainder (1/256 tsp)"))
print("-" * 100)
for ingredient, data in scaled_ingredients.items():
    #if ingredient=='milk':
    #    continue
        #print("{:<15} {:<40} {:<20.2f}".format(ingredient, data["combination"], data["remainder_256"]))
    print("{:<15} {:<60} {:<20.2f}".format(ingredient, data["combination"], data["remainder_256"]))

print("-" * 100)
print("RECETA")
print("-" * 100)
   
print("{}".format(original_ingredients["receta"]))
print("-" * 100)
