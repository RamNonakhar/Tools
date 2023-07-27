Python 3.11.3 (tags/v3.11.3:f3909b8, Apr  4 2023, 23:49:59) [MSC v.1934 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> import hou
... 
... def create_sparks_emitter(comet_geo, comet_particle_sys):
...     # Create a new node to act as the sparks emitter
...     sparks_emitter = comet_geo.createNode("popsource")
... 
...     # Rename the sparks emitter node
...     sparks_emitter.setName("sparks_emitter")
... 
...     # Set up the sparks emitter's attributes
...     sparks_emitter.parm("radx").set(0.05)  # Adjust emitter size
...     sparks_emitter.parm("rady").set(0.05)
...     sparks_emitter.parm("radz").set(0.05)
...     sparks_emitter.parm("birthrate").set(500)  # Adjust the birthrate of sparks
...     sparks_emitter.parm("life").set(1)  # Adjust the lifespan of sparks
...     sparks_emitter.parm("velx").setExpression("fit01(rand($PT), -1, 1)")  # Randomize initial velocity
...     sparks_emitter.parm("vely").setExpression("fit01(rand($PT), -1, 1)")
...     sparks_emitter.parm("velz").setExpression("fit01(rand($PT), -1, 1)")
...     sparks_emitter.parm("inherit").set(0.1)  # Make sparks inherit velocity from the comet's tail
... 
...     # Connect the sparks emitter to the comet's particle system
...     sparks_emitter.setInput(0, comet_particle_sys)
... 
... def create_debris_emitter(comet_geo, comet_particle_sys):
...     # Create a new node to act as the debris emitter
...     debris_emitter = comet_geo.createNode("popsource")
... 
...     # Rename the debris emitter node
...     debris_emitter.setName("debris_emitter")
... 
...     # Set up the debris emitter's attributes
...     debris_emitter.parm("radx").set(0.1)  # Adjust emitter size
...     debris_emitter.parm("rady").set(0.1)
...     debris_emitter.parm("radz").set(0.1)
...     debris_emitter.parm("birthrate").set(200)  # Adjust the birthrate of debris
    debris_emitter.parm("life").set(2)  # Adjust the lifespan of debris
    debris_emitter.parm("velx").setExpression("fit01(rand($PT), -2, 2)")  # Randomize initial velocity
    debris_emitter.parm("vely").setExpression("fit01(rand($PT), -2, 2)")
    debris_emitter.parm("velz").setExpression("fit01(rand($PT), -2, 2)")
    debris_emitter.parm("inherit").set(0.2)  # Make debris inherit velocity from the comet's tail

    # Connect the debris emitter to the comet's particle system
    debris_emitter.setInput(0, comet_particle_sys)

# Get the comet geometry node and its particle system
comet_geo = hou.node("/obj/comet_geo")
comet_particle_sys = comet_geo.node("particle_sys")

# Call the functions to create sparks and debris emitters
create_sparks_emitter(comet_geo, comet_particle_sys)
create_debris_emitter(comet_geo, comet_particle_sys)
