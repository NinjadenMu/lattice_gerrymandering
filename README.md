# Gerrymander a Lattice model
This program generates a n x n lattice model with realistic population and voter preference distributions.  It then gerrymanders the lattice model into a set of districts heavily favoring one party.

It uses simulated annealing and a couple of heuristics to pack districts, which is a popular method for gerrymandering.

The simulated annealing runs for 10000 iterations by default.  This should take 5-15 seconds.

You can read more about gerrymandering, the lattice model, and algorithms to gerrymander here: https://ninjadenmu.github.io/

It's a 2 part series, starting with Algorithmic Gerrymandering Pt. 1: Modelling population and voter distributions, followed by Algorithmic Gerrymandering Pt. 2: Gerrymandering the Lattice Model


  Run gerrymander.py to gerrymander a default region.  To modify the region, generate a new Region object and pass it as *region* to Gerrymander.simulated_anneal.  The definition of Region is in region.py.  To change the number of districts generated, pass the new number of districts as *districts* to Gerrymander.simulated_anneal()  The *curve* argument of Gerrymander.simulated_anneal should be a list with length *districts*.  More positive numbers in *curve* favors red, more negatives favors blue.  To pack districts, the majority of numbers in *curve* should have a small magnitude with the sign of the side to favor, and one or two districts should have a very large magnitude with the sign of the opposing side.  Simulated annealing will attempt to match the voter preference of each district to one number in *curve*.
