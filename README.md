# Gd2All
a tool for migrating GdScript to C# and c++, with features like type inference for your class declarations.  
  
#TODO: flesh out README.md

## how to update the API definition
* clone the offical godot repo
* copy it's ```doc/classes``` folder and paste it into our ```GodotAPI``` folder
* install untangle (xml parser) if you don't have it (```pip install untangle```)
* run ```py godotReference.py``` to generate the pickle class db
* profit.